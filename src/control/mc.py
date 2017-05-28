from amqp.amqplib import *
from threading import Thread
from time import time
from time import sleep
from light import Light
from rc import RemoteControl

MILLISECOND = 0.001


def current_milli_time():
    return int(round(time() * 1000))


class MotorControl(Thread):
    default = Command()
    default.set_command({"linvel": 0.0, "angvel": 0.0, "duration": 1000})

    def __init__(self, shared):
        Thread.__init__(self)
        self.autonomous = Protected()
        self.autonomous.set_value(True)

        self.rccommand = Protected()
        self.rccommand.set_value(MotorControl.default)

        self.data = shared

        self.rc = RemoteControl(self.autonomous, self.rccommand)
        self.light = Light(self.autonomous)

    def set_autonomous(self, auto):
        """
        :param Boolean auto:
        :return:
        """
        if auto:
            self.change_to_autonomous()
        else:
            self.change_to_rc()

        self.autonomous.set_value(auto)

    # Set light values here
    def change_to_rc(self):
        pass

    # Set light values here
    def change_to_autonomous(self):
        pass

    def send_motor_command(self, linear, angular):
        pass

    def run(self):
        self.rc.start()
        self.light.start()
 
        while self.data.running.get_value():

            command = {}
            duration = MILLISECOND
            if self.autonomous.get_value():
                command = self.data.commands.pop()
            else:
                command = self.rccommand.get_value()

            if len(command.keys()) == 0:
                command = MotorControl.default

            print 'Command being executed: %s' % command
            duration = command["duration"]
            linear = command["linvel"]
            angular = command["angvel"]

            # Send command here
            self.send_motor_command(linear, angular)
            starttime = current_milli_time()

            # Until command has been executed long enough or new command arrives do command
            while not self.data.new_command.get_value():
                currenttime = current_milli_time()
                if currenttime - starttime > duration:
                    break
                sleep(MILLISECOND)

        self.light.stop()
        self.rc.stop()

    def stop(self):
        self.data.running.set_value(False)