from distutils.core import setup

description = '''This package was designed to act as a driver for the 74HC165 shift register 
handling the low level operations for shifting in the status of the pins, shifting the statuses
out of the serial pin, and reading those statuses off of the serial pin.'''

setup(
    name='ShiftLib165',
    version='0.0.9',
    packages=['ShiftLib165'],
    keywords='Shift Register Driver Library 74HC165',
    url='https://github.com/superadm1n/ShiftLib165',
    license='MIT',
    author='Kyle Kowalczyk',
    author_email='kowalkyl@gmail.com',
    description='Driver for 74HC165 Shift Register',
    long_description=description,
)