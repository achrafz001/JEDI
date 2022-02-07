'''
Created on 23 avr. 2019

@author: gtexier
'''
from enum import IntEnum, unique

@unique
class Intersection(IntEnum):
    '''
    Name of the intersection types
    '''
    PathFour = 0
    PathThreeLeftFront = 1
    PathThreeRightFront = 2
    PathThreeLeftRight = 3
    PathTwoLeft = 4
    PathTwoRight = 5
    PathTwoFront = 6
    PathOne = 7
    PathZero = 8

class IntersectionError(Exception):
    pass
