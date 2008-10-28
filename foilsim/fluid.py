#!/usr/bin/env python
# encoding: utf-8
"""
fluid.py

Created by Seth Nickell on 2008-10-18.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

from simutils import *

class Fluid(object):
	# Density in kg/m^3
	def __init__(self, name, density, velocity):
		self.name = name
		self.density = density
		self.velocity = velocity


class Water(Fluid):
	def __init__(self, velocity):
		Fluid.__init__(self, "water", 1000, velocity)
		
class Air(Fluid):
	def __init__(self, velocity):
		Fluid.__init__(self, "air", 1.2, velocity)
