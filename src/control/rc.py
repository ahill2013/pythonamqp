# try:
#     import RPi.GPIO as GPIO
# except RuntimeError:
#     print("Error importing RPi.GPIO! Are you superuser (root)?")

from threading import Thread
from amqp.amqplib import Protected
from time import sleep
from time import time
import pigpio
import read_PWM


class RemoteControl(Thread):
    """
    Class where remote control is implemented. Update values provided to switch between modes
    """

    default = {"linvel": 0.00, "angvel": 0.00, "duration": 1000}

    MILLISECOND = 0.001

    PIN_SWITCH = 14  # 8
    # PIN_ESTOP = 10
    PIN_LIN = 18  # 12
    PIN_ANG = 23  # 16
    DEADZONE = .05
    RCRANGE = 400
    switch_threshold = 1700

    # Initialize GPIO
    # GPIO.setmode(GPIO.BOARD)
    pi = pigpio.pi()

    # Set pin 7 to input
    sw = read_PWM.reader(pi, PIN_SWITCH)
    lin = read_PWM.reader(pi, PIN_LIN)
    ang = read_PWM.reader(pi, PIN_ANG)

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
        sleep(.5)
        cent_lin = RemoteControl.lin.pulse_width()
        cent_ang = RemoteControl.ang.pulse_width()

        while self.running.get_value():
            # set mode to False if rc
            # set value to {linvel: value, angvel: value, duration: milliseconds}
            chlin = RemoteControl.lin.pulse_width()
            print "chlin: %f" % chlin
            chang = RemoteControl.ang.pulse_width()
            print "chang: %f" % chang
            switch = RemoteControl.sw.pulse_width()
            print "switch: %f" % switch
            if switch > RemoteControl.switch_threshold:
                self.mode.set_value(False)
                linvel = -1*(chlin-cent_lin)/RemoteControl.RCRANGE
                angvel = 1*(chang-cent_ang)/RemoteControl.RCRANGE
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
        # GPIO.cleanup()


