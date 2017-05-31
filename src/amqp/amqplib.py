import threading


class Protected(object):
    """Simple mutex protected data value"""
    # Class with simple protected value
    def __init__(self):
        self.lock = threading.Lock()
        self.value = []

    def set_value(self, val):
        self.acquire_lock()
        self.value = val
        self.release_lock()

    def get_value(self):
        self.acquire_lock()
        value = self.value
        self.release_lock()
        return value

    def pop(self):
        ret = {}
        self.acquire_lock()
        if len(self.value) > 0:
            ret = self.value.pop(0)
        self.release_lock()
        return ret

    def acquire_lock(self):
        self.lock.acquire()

    def release_lock(self):
        self.lock.release()


class Command:
    """Single Command to be executed"""
    def __init__(self):
        self.command = Protected()

    def set_command(self, command):
        self.command.set_value(command)

    def get_command(self):
        return self.command.get_value()


class Commands(object):
    """
    List of commands received by the consumer and to be executed if in autonomous mode
    """
    def __init__(self):
        self.protected = Protected()
        self.protected.set_value([])

    # Set the list of commands
    def set_commands(self, commands):
        self.protected.set_value(commands)

    # Pop a command, if none is present pop an empty dictionary
    def pop(self):
        return self.protected.pop()


class Data(object):
    """
    Datatypes shared between the consumer and the motor control
    """

    def __init__(self):
        self.commands = Commands()      # list of commands to be executed
        self.new_command = Protected()  # is there a new list of commands to be executed (true -- yes, false -- no)
        self.new_command.set_value(True)
        self.running = Protected()      # should this thread continue to run
        self.running.set_value(True)
