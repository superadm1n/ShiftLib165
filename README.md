# ShiftLib165

This project is designed to be a library to interface with a 74HC165
shift register. It handles the low level clocking, reading, and shifting
out statuses from the register.


### Prerequisites

You will need a Raspberry Pi, any model should do and the RPi.GPIO module.
If you dont have it installed on  your raspberry pi you can install it with
the following command

```
pip install RPi.GPIO
```

### Using This Project

Follow these commands to install this project into your environment

```
git clone https://github.com/superadm1n/ShiftLib165
cd ShiftLib165
python setup.py install
```

## Author

* **Kyle Kowalczyk** - [SmallGuysIT](https://smallguysit.com)



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* [Kevin Darrah](https://www.youtube.com/channel/UC42d7zFnWU0dYVk_M0JED6w) - For the awesome youtube video clearly explaining how 
the 74HC165 shift register stores and outputs data. [Video Linked Here](https://www.youtube.com/watch?v=hR6qOhUeKMc)

