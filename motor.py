#!/usr/bin/python3

import RPi.GPIO as GPIO
from time import sleep
from pins import RaspiPin
from enum import IntEnum


class MotorError(Exception):
    pass


class MotorDirection(IntEnum):
    UNDEFINED = -1
    FORWARD = 0
    BACKWARD = 1


class Motor:
    MOTOR_DELAY = 0.2
    FULL_SPEED = 1.
    STOP = 0.

    def __init__(self, battery_voltage=9.0, motor_voltage=6.0):
        if float(motor_voltage) / float(battery_voltage) > 1:
            raise MotorError("Motor voltage is higher than battery votage.")

        self.pwm_scale = float(motor_voltage) / float(battery_voltage)

        GPIO.setup(RaspiPin.LEFT_PWM_PIN, GPIO.OUT)
        self.left_pwm = GPIO.PWM(RaspiPin.LEFT_PWM_PIN, 500)
        self.left_pwm.start(0)
        GPIO.setup(RaspiPin.LEFT_1_PIN, GPIO.OUT)
        GPIO.setup(RaspiPin.LEFT_2_PIN, GPIO.OUT)

        GPIO.setup(RaspiPin.RIGHT_PWM_PIN, GPIO.OUT)
        self.right_pwm = GPIO.PWM(RaspiPin.RIGHT_PWM_PIN, 500)
        self.right_pwm.start(0)
        GPIO.setup(RaspiPin.RIGHT_1_PIN, GPIO.OUT)
        GPIO.setup(RaspiPin.RIGHT_2_PIN, GPIO.OUT)

        self.old_left_dir = MotorDirection.UNDEFINED
        self.old_right_dir = MotorDirection.UNDEFINED

    def _set_motors(self, left_pwm, left_dir: MotorDirection,
                    right_pwm, right_dir: MotorDirection):

        if self.old_left_dir != left_dir or self.old_right_dir != right_dir:
            # stop motors between sudden changes of direction
            self._set_driver_pins(self.STOP, MotorDirection.FORWARD,
                                  self.STOP, MotorDirection.FORWARD)
            sleep(self.MOTOR_DELAY)
        self._set_driver_pins(left_pwm, left_dir, right_pwm, right_dir)
        self.old_left_dir = left_dir
        self.old_right_dir = right_dir

    def _set_driver_pins(self, left_pwm, left_dir: MotorDirection,
                         right_pwm, right_dir: MotorDirection):
        if left_pwm < 0. or left_pwm > 1. or right_pwm < 0. or right_pwm > 1.:
            raise ValueError("Invalid motor speed")
        self.left_pwm.ChangeDutyCycle(left_pwm * 100 * self.pwm_scale)
        GPIO.output(RaspiPin.LEFT_1_PIN, left_dir)
        GPIO.output(RaspiPin.LEFT_2_PIN, not left_dir)

        self.right_pwm.ChangeDutyCycle(right_pwm * 100 * self.pwm_scale)
        GPIO.output(RaspiPin.RIGHT_1_PIN, right_dir)
        GPIO.output(RaspiPin.RIGHT_2_PIN, not right_dir)

    def forward(self, speed=0.5) :
        self._set_motors(speed, MotorDirection.FORWARD,
                         speed ,MotorDirection.FORWARD)

    def backward(self, speed=0.5):
        self._set_motors(speed, MotorDirection.BACKWARD,
                         speed, MotorDirection.BACKWARD)

    def stop(self):
        self._set_motors(self.STOP, MotorDirection.FORWARD,
                         self.STOP, MotorDirection.FORWARD)

    def right(self, speed=0.5):
        self._set_motors(speed, MotorDirection.FORWARD,
                         speed, MotorDirection.BACKWARD)

    def left(self, speed=0.5):
        self._set_motors(speed, MotorDirection.BACKWARD,
                         speed, MotorDirection.FORWARD)
    
    def inter_right(self, speed=0.8):
        self.forward(0.7)
        sleep(1.9)
        self._set_motors(speed, MotorDirection.FORWARD,
                         speed, MotorDirection.BACKWARD)
        sleep(1) 
#
    def inter_left(self, speed=0.8):
        self.forward(0.7)
        sleep(1.9)
        self._set_motors(speed, MotorDirection.BACKWARD,
                         speed, MotorDirection.FORWARD)
        sleep(1)
    def end_point_turn(self, speed=0.8) :

        self._set_motors(speed, MotorDirection.BACKWARD,
                         speed, MotorDirection.FORWARD)
        sleep(2.5)