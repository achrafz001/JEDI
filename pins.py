#!/usr/bin/python3

from enum import IntEnum, unique


@unique
class RaspiPin(IntEnum):
    RIGHT_PWM_PIN = 14
    RIGHT_1_PIN = 10
    RIGHT_2_PIN = 25
    LEFT_PWM_PIN = 24
    LEFT_1_PIN = 17
    LEFT_2_PIN = 4
    #SW1_PIN = 11
    #SW2_PIN = 9
    LED1_PIN = 8
    LED2_PIN = 7
    OC1_PIN = 22
    OC2_PIN = 27
    #OC2_PIN_R1 = 21
    #OC2_PIN_R2 = 27

    TRIGGER_PIN_1 = 18
    ECHO_PIN_1 = 23

    TRIGGER_PIN_2 = 2
    ECHO_PIN_2 = 3

    TRIGGER_PIN_3 = 9
    ECHO_PIN_3 = 11


class RaspiPinError(Exception):
    pass
