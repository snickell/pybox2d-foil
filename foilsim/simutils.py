#!/usr/bin/env python
# encoding: utf-8
"""
simutils.py

Created by Seth Nickell on 2008-10-13.
Copyright (c) 2008 Seth Nickell. All rights reserved.
"""

import math
from Box2D import *

_pi_div_180 = math.pi / 180.0
_180_div_pi = 180.0 / math.pi
debug = False

def radians(degrees):
	return float(degrees) * _pi_div_180
	
def degrees(radians):
	return float(radians) * _180_div_pi

def m_per_s(mph):
	return float(mph) / 2.2369

def mph(m_per_s):
	return float(m_per_s) * 2.2369

def lbs(newtons):
	return float(newtons) * 0.224808943
