import subprocess
import platform
import os

"""
From user Dan L
https://community.onion.io/topic/40/simple-python-wrapper-and-demo

Enhanced to handle:
* pin 8:  for some reason pin 8 did not respond without using fast-gpio
* added platform support

"""


class OmegaGPIOHelper(object):
    exportPath = "/sys/class/gpio/gpiochip0/subsystem/export"
    pinDirectionPath = "/sys/class/gpio/gpio$/direction"
    pinValuePath = "/sys/class/gpio/gpio$/value"
    pins = [0, 1, 6, 7, 8, 12, 13, 14, 23, 26, 21, 20, 19, 18]

    def _set_output(self, pin_number):
        if not pin_number is None:
            subprocess.call(['fast-gpio', 'set-output', str(pin_number)])

    def _set_input(self, pin_number):
        if not pin_number is None:
            subprocess.call(['fast-gpio', 'set-input', str(pin_number)])

    def _write(self, pin_number, state):
        if not pin_number is None:
            subprocess.call(['fast-gpio', 'set', str(pin_number), str(state)])

    def __init__(self):
        if platform.system() == 'Linux':
            for pin in self.pins:
                fd = open(self.exportPath, 'w')
                fd.write(str(pin))
                fd.close()

    def on(self, pin):
        self.setPin(pin, 1)

    def off(self, pin):
        self.setPin(pin, 0)

    def setPin(self, pin, value):

        if platform.system() != "Linux":
            # then we are not on the Omega, so simulate GPIO
            pin_file = "./gpio/{0}.txt".format(str(pin))
            f = open(pin_file, 'w')
            f.write(str(value))
            f.close()
            return

        # for some reason pin8 does not seem to work
        if pin == 8:
            self._set_output(value)
            self._write(8, value)
        else:
            # Set direction as out
            fd = open(self.pinDirectionPath.replace("$", str(pin)), 'w')
            fd.write("out")
            fd.close()

            # Set value
            fd = open(self.pinValuePath.replace("$", str(pin)), 'w')
            fd.write(str(value))
            fd.close()

    def getPin(self, pin):

        if platform.system() != "Linux":
            # then we are not on the Omega, so simulate GPIO
            pin_file = "./gpio/{0}.txt".format(str(pin))
            f = open(pin_file, 'r')
            value = f.readline()
            f.close()
            return int(value)

        # Set direction as in
        try:
            fd = open(self.pinDirectionPath.replace("$", str(pin)), 'w')
            fd.write("in")
            fd.close()
        except:
            pass

        # Get value
        fd = open(self.pinValuePath.replace("$", str(pin)), 'r')
        out = fd.read()
        fd.close()

        return int(out)


if __name__ == "__main__":
    pin = 8
    gpio = GPIOHelper()
    gpio.setPin(pin, 1)
    import time

    time.sleep(2)
    print("getPin: " + str(gpio.getPin(pin)))
    gpio.setPin(pin, 0)