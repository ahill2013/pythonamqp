from threading import Thread
from amqp.amqplib import Protected


class RemoteControl(Thread):
    """
    Class where remote control is implemented. Update values provided to switch between modes
    """

    def __init__(self, mode, value):
        """
        Set parameters used by motor control here
        :param Protected mode:
        :param Protected value:
        """
        Thread.__init__(self)
        self.mode = mode
        self.value = value
        self.running = Protected()
        self.running.set_value(True)

    def run(self):
        while self.running.get_value():
            # set mode to False if rc
            # set value to {linvel: value, angvel: value, duration: milliseconds}
            pass

    def stop(self):
        self.running.set_value(False)