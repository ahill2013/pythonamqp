try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! Are you superuser (root)?")

from threading import Thread
from amqp.amqplib import Protected
from time import sleep
from time import time


class RemoteControl(Thread):
    """
    Class where remote control is implemented. Update values provided to switch between modes
    """

    default = {"linvel": 0.00, "angvel": 0.00, "duration": 1000}

    MILLISECOND = 0.001

    PIN_SWITCH = 8
    # PIN_ESTOP = 10
    PIN_LIN = 12
    PIN_ANG = 14
    DEADZONE = .05
    RCRANGE = 400
    switch_threshold = 1700

    # Initialize GPIO
    GPIO.setmode(GPIO.BOARD)
    # Set pin 7 to input
    GPIO.setup(PIN_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(PIN_LIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(PIN_ANG, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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
        for x in range(0, 10):
            self.get_pwm(RemoteControl.PIN_LIN)
            self.get_pwm(RemoteControl.PIN_ANG)

        cent_lin = self.get_pwm(self.PIN_LIN)
        cent_ang = self.get_pwm(self.PIN_ANG)

        while self.running.get_value():
            # set mode to False if rc
            # set value to {linvel: value, angvel: value, duration: milliseconds}
            chlin = self.get_pwm(RemoteControl.PIN_LIN)
            chang = self.get_pwm(RemoteControl.PIN_ANG)
            switch = self.get_pwm(RemoteControl.PIN_SWITCH)
            if switch > RemoteControl.switch_threshold:
                self.mode.set_value(False)
                linvel = 1*(chlin-cent_lin)/RemoteControl.RCRANGE
                angvel = -.5*(chang-cent_ang)/RemoteControl.RCRANGE
                if linvel < RemoteControl.DEADZONE and linvel > -RemoteControl.DEADZONE:
                    linvel = 0

                if angvel < RemoteControl.DEADZONE and angvel > -RemoteControl.DEADZONE:
                    angvel = 0

                self.value.set_value({"linear": linvel, "angular": angvel, "duration": 0.002})
            else:
                self.value.set_value(RemoteControl.default)
                self.mode.set_value(True)

            sleep(RemoteControl.MILLISECOND)

    def stop(self):
        self.running.set_value(False)

    def current_nano_time(self):
        return int(round(time()*1000000))

    def get_pwm(self, pin):
        GPIO.wait_for_edge(pin, GPIO.RISING)
        start = self.current_nano_time()
        GPIO.wait_for_edge(pin, GPIO.FALLING)
        end = self.current_nano_time()
        return start - end


