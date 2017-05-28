from threading import Thread
from time import sleep
from amqp.amqplib import Protected


class Light(Thread):

    MILLISECOND = 0.001

    def __init__(self, mode):
        """
        Code for controlling the status of the light
        :param mode: Protected
        """
        Thread.__init__(self)
        self.mode = mode
        self.toggle = True
        self.running = Protected()
        self.running.set_value(True)

    def set_to_high(self):
        # set pin to high
        pass

    def set_to_low(self):
        # set pin to low
        pass

    def run(self):
        while self.running.get_value():
            if self.mode.get_value():
                if self.toggle:
                    self.set_to_low()
                    self.toggle = False
                else:
                    self.set_to_high()
                    self.toggle = True
            sleep(500 * Light.MILLISECOND)

    def stop(self):
        self.running.set_value(False)
        self.set_to_high()