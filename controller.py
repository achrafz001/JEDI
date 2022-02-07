#!/usr/bin/python3

from math import inf
from copy import error
from enum import IntEnum, unique
from time import sleep
from motor import Motor
from sensors import HCSR04, HCSR04Event



@unique
class IntersectionType(IntEnum):
    PathFour = 0
    PathThreeLeftFront = 1
    PathThreeRightFront = 2
    PathThreeLeftRight = 3
    PathTwoLeft = 4
    PathTwoRight = 5
    PathTwoFront = 6
    PathOne = 7
    PathZero = 8


class Controller:
    """Class to control motors according to sensed values.
    Note that sensing is not dependable..."""

    def __init__(self, motors: Motor, lsensor: HCSR04, fsensor: HCSR04,
                 rsensor: HCSR04, speed=0.5):
        self.motors = motors
        self.speed = speed
        self.left_sensor = lsensor
        self.front_sensor = fsensor
        self.right_sensor = rsensor

    def _get_event(self, sensor, moving=True):
        """returns a HCSR04Event according to the distance measured by the
        sensor"""
        distance = self._get_robust_distance(sensor, moving)
        if distance < sensor.low:
            return (HCSR04Event.DANGER, distance)
        elif distance < sensor.high:
            return (HCSR04Event.WALL, distance)
        else:
            return (HCSR04Event.NOTHING, distance)

    def get_left_distance(self, moving=True):
        """measures distance on the left and returns a HCSR04Event
        and the measured distance"""
        return self._get_event(self.left_sensor, moving)

    def get_front_distance(self, moving=True):
        """measures distance ahead and returns a HCSR04Event
        and the measured distance"""
        return self._get_event(self.front_sensor, moving)

    def get_right_distance(self, moving=True):
        """measures distance on the right and returns a HCSR04Event
        and the measured distance"""
        return self._get_event(self.right_sensor, moving)

    def get_robust_left_distance(self, moving=True):
        """measures distance on the left, without error, stops the droid if
        necessary"""
        return self._get_robust_distance(self.left_sensor, moving)

    def get_robust_front_distance(self, moving=True):
        """measures distance ahead, without error, stops the droid if
        necessary"""
        return self._get_robust_distance(self.front_sensor, moving)

    def get_robust_right_distance(self, moving=True):
        """measures distance on the right, without error, stops the droid if
        necessary"""
        return self._get_robust_distance(self.right_sensor, moving)

    def _get_robust_distance(self, sensor, moving=True):
        """Robust measrurement on sensor, stops motors if necessary and restart
        them according to an acceptable measurement."""
        return sensor.get_distance()

    def danger(self, le, fe, re):
        """returns True if one sensor among the three ones measures a distance
        below its lower threshold, False otherwise"""
        return ( fe is HCSR04Event.DANGER or le is HCSR04Event.DANGER
                       or re is HCSR04Event.DANGER )

    def is_exit(self, le, fe, re):
        """returns True if the maze exit is reached, False otherwise"""
        return (le is HCSR04Event.NOTHING and fe is HCSR04Event.NOTHING
                and re is HCSR04Event.NOTHING)

    def is_intersection(self, le, fe, re):
        """returns True if the droid is currently in an intersection,
        False otherwise"""
        return (le is HCSR04Event.NOTHING or re is HCSR04Event.NOTHING)

    def is_dead_end(self, le, fe, re):
        """returns True if the droid is in a dead end, False otherwise"""
        return ( le is HCSR04Event.WALL and fe is HCSR04Event.DANGER
                and re is HCSR04Event.WALL )

    def is_corridor(self, le, fe, re):
        """returns True if the Droid is in a corridor, False otherwise"""
        return (le is HCSR04Event.WALL and re is HCSR04Event.WALL 
                and fe is HCSR04Event.NOTHING )        

    def get_intersection_type(self, le, fe, re):
        """returns an IntersectionType according to the measured values on the
        three sensors"""
        if self.is_exit(le, fe, re):
            return IntersectionType.PathFour
        elif self.is_intersection(le, fe, re):
            if (le is HCSR04Event.NOTHING and fe is HCSR04Event.NOTHING and re is not HCSR04Event.NOTHING):
                return IntersectionType.PathThreeLeftFront
            elif (le is not HCSR04Event.NOTHING and fe is HCSR04Event.NOTHING
                  and re is HCSR04Event.NOTHING):
                return IntersectionType.PathThreeRightFront
            elif (le is HCSR04Event.NOTHING and fe is not HCSR04Event.NOTHING
                  and re is HCSR04Event.NOTHING):
                return IntersectionType.PathThreeLeftRight
            elif (le is HCSR04Event.NOTHING and fe is not HCSR04Event.NOTHING
                  and re is not HCSR04Event.NOTHING):
                return IntersectionType.PathTwoLeft
            elif (le is not HCSR04Event.NOTHING and
                  fe is not HCSR04Event.NOTHING and re is HCSR04Event.NOTHING):
                return IntersectionType.PathTwoRight
            else:
                raise ValueError("Unknown situation")
        elif self.is_dead_end(le, fe, re):
            return IntersectionType.PathOne
        elif self.is_corridor(le, fe, re):
            return IntersectionType.PathTwoFront
        else:
            return IntersectionType.PathZero



class PIDController(Controller):
    def __init__(self, motors: Motor,
                 lsensor: HCSR04, fsensor: HCSR04, rsensor: HCSR04,
                 speed=0.7, target=0., KP=0.02, KD=0.01, KI=0.,
                 sample_time=0.01):
        """Read https://en.wikipedia.org/wiki/PID_controller
        and https://projects.raspberrypi.org/en/projects/robotPID/5"""
        Controller.__init__(self, motors, lsensor, fsensor, rsensor, speed=speed)
        self.m1_speed = self.speed
        self.m2_speed = self.speed
        self.target = target
        print("target= {}".format(self.target))
        # https://en.wikipedia.org/wiki/PID_controller
        self.sample_time = sample_time
        self.last_sample = 0.0
        self.KP = KP
        self.KD = KD
        self.KI = KI
        self.prev_error = 0.0
        self.sum_error = 0.0      
    def adjust(self):
        """adjusts motors speeds to compensate error on objective function
        (namely a distance on left or right wall)"""    
        dist_left = self.get_robust_left_distance()
        dist_right = self.get_robust_right_distance()

        """error=  dist_right - dist_left
        if ( dist_right> 35 or dist_right == inf) :
            dist_right = 35
        elif(dist_right < -35 or dist_right == -inf) :
                dist_right = -35
        if ( dist_left> 35 or dist_left == inf) :
            dist_left = 35
        elif(dist_left < -35 or dist_left == -inf) :
            dist_left = -35
        if(error < -35 or error == -inf) :
            error = -35
        elif ( error> 35 or error == inf) :
            error = 35"""
            
        adj = (error * self.KP) + ((error-self.prev_error) * self.KD)+ (self.sum_error * self.KI)
        self.m1_speed += adj
        self.m2_speed -= adj
        print("adj",adj)
        self.m1_speed = max(min(0.8, self.m1_speed), 0.2)
        self.m2_speed = max(min(0.8, self.m2_speed), 0.2)
        sleep(self.sample_time)
        print("e1 {} m1 {}".format(dist_right, self.m1_speed))
        print("e2 {} m2 {}".format(dist_left, self.m2_speed))
        print("error1 {}".format(error))
        self.prev_error = error
        self.sum_error += error
        self.motors._set_motors(self.m1_speed,self.motors.old_left_dir,self.m2_speed,self.motors.old_right_dir)


    def go_to_the_next_intersection(self,le,fe,re):
    
        if(self.is_intersection(le,fe,re)):
            self.motors.stop()
            print("stop in intersection")    
        else :
            self.adjust()
            sleep(0.1)
        print("go next intersection")
        le,dist_left = self._get_event(self.left_sensor)
        re,dist_right = self._get_event(self.right_sensor)
        fe, dist_front = self._get_event(self.front_sensor)


        
        

        
