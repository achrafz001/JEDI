#!/usr/bin/python3

import RPi.GPIO as GPIO
import time
from enum import IntEnum
from pins import RaspiPin, RaspiPinError
from math import inf


class HCSR04Event(IntEnum):
    DANGER = 0
    WALL = 1
    NOTHING = 2

    def __repr__(self):
        return self.name


class HCSR04:
    def __init__(self, name, echo: RaspiPin, trigger: RaspiPin, low=10., high=100.):
        self.name = name
        if echo is None:
            raise RaspiPinError(self.name+" "+"Echo pin not set")
        self.echo = echo
        if trigger is None:
            raise RaspiPinError(self.name+" "+"Trigger pin not set")
        self.trigger = trigger
        self.low = low
        self.high = high
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def _send_trigger_pulse(self, wait_duration=0.00001):
        GPIO.output(self.trigger, GPIO.LOW)
        time.sleep(0.2)
        GPIO.output(self.trigger, GPIO.HIGH)
        time.sleep(wait_duration)
        GPIO.output(self.trigger, GPIO.LOW)

    def _wait_for_echo(self, value, timeout):
        count = timeout
        while GPIO.input(self.echo) == value and count > 0:
            count -= 1
        return count

    def get_distance(self, threshold=100.):
        # print("Sending pulse", time.time())
        self._send_trigger_pulse()
        self._wait_for_echo(GPIO.LOW, 10000)
        start = time.time()
        # print("Got HIGH echo at", start)
        count2 = self._wait_for_echo(GPIO.HIGH, 10000)
        finish = time.time()
        # print("Got LOW echo at", finish)
        pulse_len = finish - start
        distance_cm = pulse_len * 34300. / 2.
        # print(count1, count2, pulse_len, distance_cm)
        if distance_cm > self.high:
            distance_cm = 120
        return distance_cm
        #blaff
