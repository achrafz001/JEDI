#!/usr/bin/python3

from cgi import print_directory
import sys
from time import sleep
import tty
import termios
from enum import IntEnum, unique
from turtle import right
import RPi.GPIO as GPIO
from motor import Motor
from sensors import HCSR04 
from controller import PIDController , IntersectionType, HCSR04Event
from pins import RaspiPin, RaspiPinError

class Droid:
    def __init__(self, battery_voltage=9.0, motor_voltage=6.0, warn=True,
                 speed=0.5):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(warn)
        self.speed = speed
        self.motors = Motor(battery_voltage, motor_voltage)

    def __del__(self):
        self._cleanup()

    def _set_led1(self, state):
        GPIO.output(RaspiPin.LED1_PIN, state)

    def _set_led2(self, state):
        GPIO.output(RaspiPin.LED2_PIN, state)

    def _set_oc1(self, state):
        GPIO.output(RaspiPin.OC1_PIN, state)

    def _set_oc2(self, state):
        GPIO.output(RaspiPin.OC2_PIN, state)

    def _cleanup(self):
        GPIO.cleanup()

    def forward(self):
        self.motors.forward(speed=self.speed)

    def backward(self):
        self.motors.backward(speed=self.speed)

    def stop(self):
        self.motors.stop()

    def right(self):
        self.motors.right(speed=self.speed)

    def left(self):
        self.motors.left(speed=self.speed)


class RoverKey(IntEnum):
    UP = 0
    DOWN = 1
    RIGHT = 2
    LEFT = 3
    STOP = 4


class RoverDroid(Droid):
    def __init__(self, battery_voltage=9.0, motor_voltage=6.0, warn=True,
                 speed=0.5):
        Droid.__init__(self, battery_voltage, motor_voltage, warn, speed)

    def _read_char(self):
        """Read chars from keyboard"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        if ch == '0x03':
            raise KeyboardInterrupt
        return ch

    def _read_key(self):
        """Converts keys from keyboard to directions to the droid"""
        c1 = self._read_char()
        if ord(c1) != 0x1b:
            # escape char
            return RoverKey.STOP
        c2 = self._read_char()
        if ord(c2) != 0x5b:
            # [ char
            raise KeyboardInterrupt
        c3 = self._read_char()
        return RoverKey(ord(c3) - 65)  # 0=Up, 1=Down, 2=Right, 3=Left arrows

    def run(self):
        """Continuously read keys stroke from the keyboard and applies
        directions to current droid"""
        try:
            print("Use the arrow keys to move the robot")
            print("Press CTRL-c to quit the program")
            while True:
                key = self._read_key()
                if key is RoverKey.UP:
                    print("ROVER", "FORWARD")
                    self.forward()
                elif key is RoverKey.DOWN:
                    print("ROVER", "BACKWARD")
                    self.backward()
                elif key is RoverKey.LEFT:
                    print("ROVER", "TURN LEFT")
                    self.left()
                elif key is RoverKey.RIGHT:
                    print("ROVER", "TURN RIGHT")
                    self.right()
                elif key is RoverKey.STOP:
                    print("ROVER", "STOP")
                    self.stop()
                else:
                    print("ROVER", "UNKNOWN VALUE:", key)
                    raise KeyboardInterrupt
        except KeyboardInterrupt:
            self._cleanup()


class Droid3Sensors(RoverDroid):
    """Class to explore a maze with a controller to drives motors according to
    sensors"""

    def __init__(self, battery_voltage=9.0, motor_voltage=6.0, warn=True,
                 speed=0.5, low=15., high=50., target=20., KP=0.02, KD=0.01,
                 KI=0., sample_time=0.01):
        Droid.__init__(self, battery_voltage, motor_voltage, warn, speed)
        print("Robot 3 Sensors with controller", "speed=%02f" % speed)
        self.left_sensor = HCSR04("LEFT", RaspiPin.ECHO_PIN_3,
                                  RaspiPin.TRIGGER_PIN_3, low=low, high=high)
        self.front_sensor = HCSR04("FRONT", RaspiPin.ECHO_PIN_1,
                                   RaspiPin.TRIGGER_PIN_1, low=2*low, high=high)
        self.right_sensor = HCSR04("RIGHT", RaspiPin.ECHO_PIN_2,
                                   RaspiPin.TRIGGER_PIN_2, low=low, high=high)
        self.controller = PIDController(self.motors, self.left_sensor,
                                        self.front_sensor, self.right_sensor,
                                        speed=speed, target=target, KP=KP,
                                        KD=KD, KI=KI, sample_time=sample_time)

    def intersection (self, inter) :
        print("is intersection")
        if inter is IntersectionType.PathThreeLeftFront :
            self.forward(0.6)
            sleep(2)
        elif ( inter is IntersectionType.PathThreeRightFront) :
            self.motors.inter_right()
            print("right inter")
        elif ( inter is IntersectionType.PathThreeLeftRight) :
            self.motors.inter_right()
        elif ( inter is IntersectionType.PathTwoLeft) :
            self.motors.inter_left()
        elif( inter is IntersectionType.PathTwoRight) :
            self.motors.inter_right()
        elif( self.controller.danger()) :
            self.motors.end_point_turn()
        else :
            self.stop()
            self.backward()
            self.controller.adjust()
            self.stop()

    def explore(self) :
        """Explores maze until the exit is found""" 
        try:
            print("Use the arrow keys to move the robot")
            print("Press CTRL-c to quit the program")
            le,dist_left = self.controller._get_event(self.left_sensor)
            re,dist_right = self.controller._get_event(self.right_sensor)
            fe, dist_front = self.controller._get_event(self.front_sensor)
            while (not self.controller.is_exit(le,fe,re)) :
                self.forward()
                self.controller.go_to_the_next_intersection(le,fe,re)
                print("left dist",self.controller.get_robust_left_distance())
                print("right dist",self.controller.get_robust_left_distance())
                if (self.controller.is_intersection(le,fe,re)) :
                    self.intersection(self.controller.get_intersection_type(le,fe,re))
                elif (self.controller.is_dead_end(le,fe,re)) :
                    self.motors.end_point_turn()
                    print("dead endooo")
                le,dist_left = self.controller._get_event(self.left_sensor)
                re,dist_right = self.controller._get_event(self.right_sensor)
                fe, dist_front = self.controller._get_event(self.front_sensor)
        except KeyboardInterrupt:
            self._cleanup()





    """
    2nd version
    def explore(self) :

    try:
        print("Use the arrow keys to move the robot")
        print("Press CTRL-c to quit the program")
        le,dist_left = self.controller._get_event(self.left_sensor)
        re,dist_right = self.controller._get_event(self.right_sensor)
        fe, dist_front = self.controller._get_event(self.front_sensor)
        i = 0

        while True:
            print("dist",dist_front )
            self.forward()
            self.controller.adjust()
            sleep(0.09)

            if(self.controller.danger(le,fe,re)):

                if( le is HCSR04Event.DANGER and re is not HCSR04Event.DANGER ) :
                    
                    self.motors.right(0.8)
                    sleep(1)
                    self.stop()
                elif(re is HCSR04Event.DANGER) :
                    
                    self.motors.left(0.8)
                    sleep(1)
                    self.stop()
                elif (self.controller.is_dead_end(le,fe,re)) :
                    self.motors.end_point_turn()
                    self.stop()
                else :
                    self.motors.right(0.8)
                    sleep(1)
                    self.stop()
            
            
            
            le,dist_left = self.controller._get_event(self.left_sensor)
            re,dist_right = self.controller._get_event(self.right_sensor)
            fe, dist_front = self.controller._get_event(self.front_sensor)
            
    except KeyboardInterrupt:
        self._cleanup()  

  """
            
            
            
    """
    3rd version        
    def explore(self) :
        #Explores maze until the exit is found
        try:
            print("Use the arrow keys to move the robot")
            print("Press CTRL-c to quit the program")
            le = self.controller._get_event(self.left_sensor)
            re = self.controller._get_event(self.right_sensor)
            fe = self.controller._get_event(self.front_sensor)
            while (not self.controller.is_exit(le,fe,re)) :
                while (not self.controller.is_intersection(le,fe,re)) :
                    self.forward()
                    self.controller.adjust()
                    sleep(0.1)
                if (self.controller.is_intersection()) :
                    self.stop()
                    self.intersection(self.controller.get_intersection_type(le,fe,re))
                elif (self.controller.is_dead_end(le,fe,re)) :
                    self.stop()
                    self.motors.end_point_turn()

        except KeyboardInterrupt:
            self._cleanup() """
            