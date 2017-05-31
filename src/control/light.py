try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! Are you superuser (root)?")

from threading import Thread
from time import sleep
from amqp.amqplib import Protected


class Light(Thread):
    MILLISECOND = 0.001
    PIN_LIGHT = 5

    # Initialize GPIO
    GPIO.setmode(GPIO.BOARD)
    # Set pin 5 to output
    GPIO.setup(PIN_LIGHT, GPIO.OUT, initial=GPIO.HIGH)

    def __init__(self, mode):
        """
        Code for controlling the status of the light
        :param mode: Protected
        """
        Thread.__init__(self)
        self.mode = mode
        self.running = Protected()
        self.running.set_value(True)

    @staticmethod
    def set_to_high():
        # set pin to high
        GPIO.output(Light.PIN_LIGHT, GPIO.HIGH)
        pass

    @staticmethod
    def set_toggle():
        # set pin to low
        GPIO.output(Light.PIN_LIGHT, not GPIO.input(Light.PIN_LIGHT))
        pass

    def run(self):
        while self.running.get_value():  # While thread is running
            if not self.mode.get_value():  # Get mode: RC or auto (false, true). If RC (false), then -
                self.set_to_high()  # - Toggle the light --
            else:  # Else if auto (true), then -
                self.set_toggle()  # - Set the light solid high
            sleep(500 * Light.MILLISECOND)  # -- Every 500 milliseconds

    def stop(self):
        self.running.set_value(False)
        self.set_to_high()
        GPIO.cleanup(Light.PIN_LIGHT)
