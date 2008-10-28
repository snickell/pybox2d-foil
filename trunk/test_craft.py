#!/usr/bin/python
#
# C++ version Copyright (c) 2006-2007 Erin Catto http://www.gphysics.com
# Python version Copyright (c) 2008 kne / sirkne at gmail dot com
# 
# Implemented using the pybox2d SWIG interface for Box2D (pybox2d.googlepages.com)
# 
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
# 1. The origin of this software must not be misrepresented; you must not
# claim that you wrote the original software. If you use this software
# in a product, an acknowledgment in the product documentation would be
# appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

import pygame
from pygame.locals import *
import test_main
from test_main import box2d

from foilsim import *
from foilsim.simutils import *

import math

from operator import add

class Masheet(test_main.Framework):
	"""You can use this class as an outline for your tests.

	"""		
	name = "Craft" # Name of the class to display
	def __init__(self):
		""" 
		Initialize all of your objects here.
		Be sure to call the Framework's initializer first.
		"""
		super(Masheet, self).__init__()

		self.world.SetGravity(b2Vec2(0.0, 0.0))

		# Initialize all of the objects
		self.craft = Craft(m_per_s(30), 10, self.world)
		self.craft.step()

		self.viewZoom = 20
		self.updateCenter()
		
		pygame.joystick.init()
		if pygame.joystick.get_count() > 0: 
			self.joystick = pygame.joystick.Joystick(0)
		else:
			self.joystick = None
		self.joystick.init()
			
	def Keyboard(self, key):
		"""
		The key is from pygame.locals.K_*
		(e.g., if key == K_z: ... )
		"""
		if key == pygame.K_a: self.craft.hydrofoil.rotate_wing(radians(1.0))
		elif key == pygame.K_s: self.craft.hydrofoil.rotate_wing(radians(-1.0))
		elif key == pygame.K_q: self.craft.airfoil.rotate_wing(radians(1.0))
		elif key == pygame.K_w: self.craft.airfoil.rotate_wing(radians(-1.0))
		elif key == pygame.K_1: self.fluid.velocity -= velocity_5_mph
		elif key == pygame.K_2: self.fluid.velocity += velocity_5_mph
		#print "Wind Speed: %3.2fmph, Attack: %3.2f" % (mph(self.fluid.velocity.Length()), degrees(self.wing_angle))
		pass

	def Step(self, settings):
		"""Called upon every step.
		You should always call
		 -> super(Your_Test_Class, self).Step(settings)
		at the _end_ of your function.
		"""

		self.gui_table.updateSettings(settings)

		airfoil_angle = self.joystick.get_axis(0) * 10.0
		self.craft.airfoil.set_wing_angle(radians(airfoil_angle))
		hydrofoil_angle = self.joystick.get_axis(2) * 10.0
		self.craft.hydrofoil.set_wing_angle(radians(hydrofoil_angle))

		# do stuff        
		self.craft.step()
		
		if settings.draw:
			self.DrawString(0,self.textLine,"Use a and s to rotate the hydrofoil, q and w to rotate the airfoil")
			self.textLine+=15
			v = self.craft.velocity()
			relative_v = mph(v.Length())
			force = reduce(add, [d[0] for d in self.craft.get_force_vectors()])
			self.DrawString(0,self.textLine, "Absolute Velocity (mph) : %3.1f" % mph(relative_v))
			self.textLine+=15
			self.DrawString(0,self.textLine, "Windspeed (mph): %4.1f    Angle to wind: %4.1f" % (mph(self.craft.windspeed()), degrees(math.atan2(v.y, v.x))))
			self.textLine+=15
			self.DrawString(0,self.textLine, "Force (lbs): %5.0f,%5.0f" % (lbs(force.x), lbs(force.y)))
			self.textLine+=15			
			if mph(relative_v) > 58.2:
				self.textLine+=15				
				self.DrawString(0,self.textLine, "RECORD PACE")
				self.textLine+=15
		
		super(Masheet, self).Step(settings)

		if settings.draw:
			center = self.craft.get_center()
			self.viewCenter = center * self.viewZoom
			self.updateCenter()

			# draw velocity vector
			print v
			self.debugDraw.DrawSegment(center, center + v, box2d.b2Color(1.0, 1.0, 1.0))

			for force in self.craft.get_force_vectors():
				world_force, world_point, color = force
				self.debugDraw.DrawSegment(world_point, world_point + (world_force / 100.0), color)

		self.craft.clear_force_vectors()

	def JointDestroyed(self, joint):
		"""
		The joint passed in was removed.
		"""
		print "BOOM!"
		pass


	def BoundaryViolated(self, body):
		"""
		The body went out of the world's extents.
		"""
		pass

if __name__=="__main__":
	test_main.main(Masheet)

