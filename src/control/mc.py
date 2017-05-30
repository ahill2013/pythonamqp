from amqp.amqplib import *
from threading import Thread
from time import time
from time import sleep
from light import Light
from rc import RemoteControl
from roboclaw import Roboclaw
import math

MILLISECOND = 0.001

DIFFERENTIAL_MODEL_L = 0.7747   # distance between wheels (axle length)
DIFFERENTIAL_MODEL_R = 0.166    # radius of the wheels

RC = False
AUTONOMOUS = True
TICKS_PER_REV = 753.2   # encoder ticks for one revolution of wheel
QPPS = 4000 # max velocity in ticks per second

# PID constants
P = 1
I = 0
D = 0

ACCEL = 2000 # acceleration rate in ticks/sec^2


def current_milli_time():
    return int(round(time() * 1000))


class MotorControl(Thread):
    default = {"linvel": 0.00, "angvel": 0.00, "duration": 1000}
    claw = Roboclaw("/dev/roboclaw", 115200)
    claw.Open()
    ADDRESS = 0x80

    def __init__(self, shared):
        Thread.__init__(self)
        self.mode = Protected()
        self.mode.set_value(AUTONOMOUS)

        self.rccommand = Protected()  # most recently set rc command
        self.rccommand.set_value(MotorControl.default)

        self.shared = shared

        self.rc = RemoteControl(self.mode, self.rccommand)
        self.light = Light(self.mode)
        MotorControl.claw.SetM1VelocityPID(MotorControl.ADDRESS, P, I, D, QPPS)
        MotorControl.claw.SetM2VelocityPID(MotorControl.ADDRESS, P, I, D, QPPS)

    def set_mode(self, mode_):
        self.mode.set_value(mode_)

        if mode_:
            self.autonomous_mode()
        else:
            self.rc_mode()

    def get_mode(self):
        return self.mode.get_value()

    def rc_mode(self):
        pass

    def autonomous_mode(self):
        pass

    @staticmethod
    # Given linear and angular velocities return the desired speed of the left wheel
    def get_left_speed(lin, ang):
        return ((lin / DIFFERENTIAL_MODEL_R) - DIFFERENTIAL_MODEL_L * ang) / (2 * DIFFERENTIAL_MODEL_R)

    @staticmethod
    # Given linear and angular velocities return the desired speed of the right wheel
    def get_right_speed(lin, ang):
        return ((lin / DIFFERENTIAL_MODEL_R) + DIFFERENTIAL_MODEL_L * ang) / (2 * DIFFERENTIAL_MODEL_R)

    def send_motor_command(self, linear, angular):
        left_vel = int(round(MotorControl.get_left_speed(linear, angular)*TICKS_PER_REV/(2*math.pi)))
        right_vel = int(round(MotorControl.get_right_speed(linear, angular)*TICKS_PER_REV/(2*math.pi)))
        MotorControl.claw.SpeedAccelM1M2(MotorControl.ADDRESS, ACCEL, left_vel, right_vel)

    def run(self):
        self.rc.start()
        self.light.start()

        while self.shared.running.get_value():

            command = {}
            duration = MILLISECOND
            if self.get_mode():                           # If in auto
                self.shared.new_command.set_value(False)  # set new commands to false
                command = self.shared.commands.pop()      # get a command from amqp queue
                if len(command.keys()) == 0:              # If there are no commands in amqp queue -
                    command = MotorControl.default        # - use the default command (stop)
            else:
                self.shared.commands.set_commands([])
                command = self.rccommand.get_value()

            print 'Command being executed: %s' % command
            duration = command["duration"]
            linear = command["linvel"]
            angular = command["angvel"]

            # Send command here
            self.send_motor_command(linear, angular)
            starttime = current_milli_time()  # time at start of loop, measure duration of command by comparing
            # current time to this time

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
