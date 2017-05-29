from amqp.amqplib import *
from threading import Thread
from time import time
from time import sleep
from light import Light
from rc import RemoteControl

MILLISECOND = 0.001

DIFFERENTIAL_MDOEL_L = 0.7747   # distance between wheels (axle length)
DIFFERENTIAL_MDOEL_R = 0.166    # radius of the wheels


def current_milli_time():
    return int(round(time() * 1000))


class MotorControl(Thread):
    default = {"linvel": 0.00, "angvel": 0.00, "duration": 1000}

    def __init__(self, shared):
        Thread.__init__(self)
        self.mode = Protected()
        self.mode.set_value(True)

        self.rccommand = Protected() # most recently set rc command
        self.rccommand.set_value(MotorControl.default)

        self.shared = shared

        self.rc = RemoteControl(self.mode, self.rccommand)
        self.light = Light(self.mode)

    def set_mode(self, auto):
        """
        :param Boolean auto:
        :return:
        """
        if auto:
            self.change_to_autonomous()
        else:
            self.change_to_rc()

        self.mode.set_value(auto)

    # Set light values here
    def change_to_rc(self):
        pass

    # Set light values here
    def change_to_autonomous(self):
        pass

    @staticmethod
    # Given linear and angular velocities return the desired speed of the left wheel
    def get_left_speed(lin, ang):
        return ((lin / DIFFERENTIAL_MDOEL_R) - DIFFERENTIAL_MDOEL_L * ang) / (2 * DIFFERENTIAL_MDOEL_R)

    @staticmethod
    # Given linear and angular velocities return the desired speed of the right wheel
    def get_right_speed(lin, ang):
        return ((lin / DIFFERENTIAL_MDOEL_R) + DIFFERENTIAL_MDOEL_L * ang) / (2 * DIFFERENTIAL_MDOEL_R)

    def send_motor_command(self, linear, angular):
        pass

    def run(self):
        self.rc.start()
        self.light.start()

        while self.shared.running.get_value():

            command = {}
            duration = MILLISECOND
            if self.mode.get_value():                     # If in auto
                self.shared.new_command.set_value(False)  # set new commands to false
                command = self.shared.commands.pop()      # get a command from amqp queue
                if len(command.keys()) == 0:              # If there are no commands in amqp queue -
                    command = MotorControl.default        # - use the default command (stop)
            else:
                command = self.rccommand.get_value()

            print 'Command being executed: %s' % command
            duration = command["duration"]
            linear = command["linvel"]
            angular = command["angvel"]

            # Send command here
            self.send_motor_command(linear, angular)
            starttime = current_milli_time() # time at start of loop, measure duration of command by comparing current
                                             # time to this time

            # Until command has been executed long enough or new command arrives do command
            while not self.shared.running.get_value() and self.shared.new_command.get_value():
                currenttime = current_milli_time()

                # if command has been executed for the duration specified exit and get new command
                if currenttime - starttime > duration:
                    print "breaking"
                    break
                sleep(2 * MILLISECOND)  # sleep two milliseconds and check again
            print "Getting next command"

        self.light.stop()
        self.rc.stop()

    # kill thread
    def stop(self):
        self.shared.running.set_value(False)
