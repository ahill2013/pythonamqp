# try:
#     import RPi.GPIO as GPIO
# except RuntimeError:
#     print("Error importing RPi.GPIO! Are you superuser (root)?")

from threading import Thread
from amqp.amqplib import Protected
from time import sleep
from time import time
import pigpio


class RemoteControl(Thread):
    """
    Class where remote control is implemented. Update values provided to switch between modes
    """

    default = {"linvel": 0.00, "angvel": 0.00, "duration": 1000}

    MILLISECOND = 0.001

    PIN_SWITCH = 8
    # PIN_ESTOP = 10
    PIN_LIN = 12
    PIN_ANG = 16
    DEADZONE = .05
    RCRANGE = 400
    switch_threshold = 1700

    # Initialize GPIO
    # GPIO.setmode(GPIO.BOARD)
    pi = pigpio.pi()
    # Set pin 7 to input
    pi.set_mode(PIN_SWITCH, pigpio.INPUT)
    pi.set_mode(PIN_LIN, pigpio.INPUT)
    pi.set_mode(PIN_ANG, pigpio.INPUT)
    pi.set_pull_up_down(PIN_SWITCH, pigpio.PUD_DOWN)
    pi.set_pull_up_down(PIN_LIN, pigpio.PUD_DOWN)
    pi.set_pull_up_down(PIN_ANG, pigpio.PUD_DOWN)
    sw = pi.callback(PIN_SWITCH, pigpio.EITHER_EDGE)
    lin = pi.callback(PIN_LIN, pigpio.EITHER_EDGE)
    ang = pi.callback(PIN_ANG, pigpio.EITHER_EDGE)

    # GPIO.setup(PIN_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.setup(PIN_LIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.setup(PIN_ANG, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def __init__(self, mode, value):
        """
        Set parameters used by motor control here
        :param Protected mode:
        :param Protected value:
        """
        Thread.__init__(self)
        self.mode = mode  # TODO: make this get value from controller
        self.value = value
        self.running = Protected()
        self.running.set_value(True)

    def get_mode(self):
        return self.mode.get_value()

    def run(self):
        print "Entered run in rc"
        for x in range(0, 10):
            self.get_pwm(RemoteControl.lin)
            self.get_pwm(RemoteControl.ang)

        cent_lin = self.get_pwm(self.lin)
        cent_ang = self.get_pwm(self.ang)

        while self.running.get_value():
            # set mode to False if rc
            # set value to {linvel: value, angvel: value, duration: milliseconds}
            chlin = self.get_pwm(RemoteControl.lin)
            print "chlin: %f" % chlin
            chang = self.get_pwm(RemoteControl.ang)
            print "chang: %f" % chang
            switch = self.get_pwm(RemoteControl.sw)
            print "switch: %f" % switch
            if switch > RemoteControl.switch_threshold:
                self.mode.set_value(False)
                linvel = 1*(chlin-cent_lin)/RemoteControl.RCRANGE
                angvel = -.5*(chang-cent_ang)/RemoteControl.RCRANGE
                if RemoteControl.DEADZONE > linvel > -RemoteControl.DEADZONE:
                    linvel = 0

                if RemoteControl.DEADZONE > angvel > -RemoteControl.DEADZONE:
                    angvel = 0

                self.value.set_value({"linvel": linvel, "angvel": angvel, "duration": 0.002})
            else:
                self.value.set_value(RemoteControl.default)
                self.mode.set_value(True)

            sleep(RemoteControl.MILLISECOND)

    def stop(self):
        self.running.set_value(False)
        GPIO.cleanup()

    @staticmethod
    def current_nano_time():
        return int(round(time()*1000000))

    def get_pwm(self, pin):
        while pin.level != 1:
            start = pin.tick
        while pin.level != 0:
            end = pin.tick
        return end - start


