'''
MIT License

Copyright (c) 2018 Kyle Kowalczyk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Code contained in this module is specific to handeling the low level operations when interfacing with
a 74HC165 PISO Shift register
'''

import RPi.GPIO as io
import time


class ShiftReg():

    '''
    This class contains the code that on a low level handles interfacing with the register.
    It takes care of loading values into the register and reading the values out of the register
    '''

    def __init__(self, serial_out, load_pin, clock_enable, clock_pin, warnings=False, bitcount=8):

        '''

        :param serial_out: BCM GPIO pin that's connected to chip pin 9 (Serial Out)
        :param load_pin: BCM GPIO pin that's connected to chip pin 1 (PL)
        :param clock_enable: BCM GPIO pin that's connected to chip pin 15 (Clock enable) not required
        :param clock_pin: BCM GPIO pin that's connected to chip pin 2 (Clock Pin
        :param warnings:
        :param bitcount:
        '''


        io.setwarnings(warnings)
        io.setmode(io.BCM)
        self.data_pin = serial_out
        self.load_reg_pin = load_pin

        self.clock_pin = clock_pin
        self.clock_enable = clock_enable
        self._gpio_init()

        self.bitcount = bitcount

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.clean_gpio()

    def _gpio_init(self):

        '''Sets up GPIO pins for output and gives them their default value

        :return: Nothing
        '''

        # sets GPIO pins for output
        io.setup(self.data_pin, io.IN, pull_up_down=io.PUD_DOWN)
        io.setup(self.clock_pin, io.OUT)
        io.setup(self.clock_enable, io.OUT)
        io.setup(self.load_reg_pin, io.OUT)

        # sets default values on GPIO pins

        io.output(self.clock_pin, 0)
        io.output(self.clock_enable, 0)
        io.output(self.load_reg_pin, 1)


    def _read_input(self):

        '''This method will read the value on the serial out pin from the
        register

        :return: Value read from the register
        '''

        status = io.input(self.data_pin)

        return status

    def _cycle_clock(self, n=1):

        '''This method will cycle the clock pin high and low to shift
        the data down the register

        :param n: Number of times to cycle clock (Default 1 time)
        :return:
        '''

        self._shift_register(n)

    def _shift_register(self, n=1):

        ''' This method cycles the clock pin high and low which
        shifts the register down.

        :param n: number of times to cycle the clock pin (default 1 time)
        :return:
        '''

        for x in range(n):
            io.output(self.clock_pin, 1)
            io.output(self.clock_pin, 0)

    def read_register(self):

        '''This method handles reading the data out of the entire register.
        It loads the values into the register, shifts all of the values out of the
        register and reads the values storing them in a list left to right starting
        at Pin 0 going to the highest pin in your chain

        :return: List of pin values from the register lowest to highest pin.
        '''

        register = []

        # Loads the status of the input pins into the internal register
        self._load_register()

        # shifts out each bit and stores the value
        for x in range(self.bitcount):
            # Stores the value of the pin
            register.append(self._read_input())

            # Cycles the clock causing the register to shift
            self._shift_register()

        # reverses the list so it reads from left to right pin0 - pin7
        register.reverse()

        return register


    def _load_register(self):

        '''This method takes the values on the input pins of the register and loads
        them into the internal storage register in preperation to be shifted out of the
        serial port

        :return: Nothing
        '''

        io.output(self.load_reg_pin, 0)
        io.output(self.load_reg_pin, 1)



    def clean_gpio(self):

        '''This method cleans up the GPIO pins, it should be run whenever you are done
        interfacing with the GPIO pins like at the end of the script/program.

        :return:
        '''

        io.cleanup()


class ReadHandler(ShiftReg):

    '''
    This class contains code that should be used when taking input from devices that multiple
    inputs could change state in the same read cycle. Interfacing with buttons would not
    be a good use case but interfacing with other electronics would be.
    '''

    def __init__(self, serial_out, load_pin, clock_enable, clock_pin, warnings=False, bitcount=8):

        '''

        :param serial_out: BCM GPIO pin that's connected to chip pin 9 (Serial Out)
        :type serial_out: int
        :param load_pin: BCM GPIO pin that's connected to chip pin 1 (PL)
        :type load_pin: int
        :param clock_enable: BCM GPIO pin that's connected to chip pin 15 (Clock enable) not required
        :type clock_enable: int
        :param clock_pin: BCM GPIO pin that's connected to chip pin 2 (Clock Pin
        :type clock_pin: int
        :param warnings: Default set to false to supress any GPIO warnings
        :type warnings: bool
        :param bitcount: Number of bits in your register/register chain. ex. 1 register = 8; 2 = 16
        :type bitcount: int
        '''

        ShiftReg.__init__(self, serial_out, load_pin, clock_enable, clock_pin, warnings, bitcount)

        # reads the status of the input registers on initilization so it has a basline to go off of
        self.last_reading = self.read_register()
        self.loop_breaker = False

    def _detect_changed_pins(self, reading, last_reading):

        '''This method is responsible for detecting changes in the state of the pins.
        It will detect if a pin was previously in an up state and changed to down and
        also if it was previously in a down state and changed to up.

        :param reading: The current reading of the state of the pins
        :param last_reading: The previous reading of the state of the pins
        :return: A list of the pins that were changed up and a list of the pins that were changed down.
        '''

        pins_changed_up = []
        pins_changed_down = []

        for x in range(self.bitcount):
            if reading[x] != last_reading[x]:
                if reading[x] == 1:
                    pins_changed_up.append(x)
                else:
                    pins_changed_down.append(x)

        return pins_changed_up, pins_changed_down

    def _callback(self, pins_changed_up, pins_changed_down):

        '''This method is the call back for status changes. it will pass the list of the pins
        that changed to their corresponding functions to enable handle the pins differently on
        an up status and on a down status.

        :param pins_changed_up: list of pins that were changed from an up status to a down status
        :type pins_changed_up: list
        :param pins_changed_down: List of pins that were changed from a down status to an up status
        :type pins_changed_down: list
        :return: Nothing
        '''

        for pin in pins_changed_up:
            self.handle_on_up(pin)

        for pin in pins_changed_down:
            self.handle_on_down(pin)


    def handle_on_up(self, pin):

        '''This method is meant to be overwritten in a child class to handle code when a
        pins status is changed from down to up.

        :param pin: list of the pins that were changed from a down status to an up status
        :type pin: int
        :return: Nothing
        '''

        print('handling on up')
        print(pin)

    def handle_on_down(self, pin):

        '''This method is meant to be overwritten in a child class to handle code
        when a pins status is changed from up to down.

        :param pin: List of the pins that were changed from an up status do a down status
        :type pin: int
        :return: Nothing
        '''

        print('handling on down')
        print(pin)


    def watch_inputs(self):

        '''This method will loop to gather the status of the pins on the register and handle them accordingly
        To break out of this loop set the class attribute self.loop_breaker to True

        :return: Nothing
        '''

        while True:

            reading = self.read_register()

            if reading != self.last_reading:
                pins_changed_up, pins_changed_down = self._detect_changed_pins(reading, self.last_reading)
                self._callback(pins_changed_up, pins_changed_down)

                self.last_reading = reading

            if self.loop_breaker == True:
                break


if __name__ == '__main__':

    '''
    This class serves as an example how to interface with the code above when trying to drop into a
    loop to read the input from a register. All we need to do is overwrite the handle_on_up and 
    handle_on_down methods and we can read input from our input register and dont have to worry
    about any low level handling.
    '''
    class Test(ReadHandler):
        def __init__(self, serial_out, load_pin, clock_enable, clock_pin, warnings=False, bitcount=8):
            ReadHandler.__init__(self, serial_out, load_pin, clock_enable, clock_pin, warnings, bitcount)

        def handle_on_up(self, pin):
            print('Pin {} has been changed to UP'.format(pin))

        def handle_on_down(self, pin):
            print('Pin {} has been changed to DOWN'.format(pin))
        

    with Test(26, 4, 6, 5) as t:
        try:
            t.watch_inputs()
        except KeyboardInterrupt:
            t.loop_breaker = True
            print('\nBroke Loop')
    '''
    t = ShiftReg(26, 4, 6, 5)
    while True:
        try:
            reg = t.read_register()
            print(reg, end='\r')
            time.sleep(.2)
        except KeyboardInterrupt:
            break
    t.clean_gpio()
    '''
