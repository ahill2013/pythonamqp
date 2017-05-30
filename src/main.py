#!/usr/bin/python

from amqp.consumer import MCConsumer
from amqp.amqplib import Data
from amqp.consumer import get_format
from control.mc import MotorControl
import logging

logging.basicConfig(level=logging.INFO, format=get_format())

data = Data()
control = MotorControl(data)
consumer = MCConsumer('amqp://ubuntu:ubuntu@192.168.11.4:5672/%2F', data)
try:
    consumer.start()
    control.start()
    
except KeyboardInterrupt:
    consumer.stop()
    control.stop()


