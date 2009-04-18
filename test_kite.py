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

velocity_20_mph = box2d.b2Vec2(-8.94, 0.0)
velocity_5_mph = velocity_20_mph / 4.0

class Masheet(test_main.Framework):
	"""You can use this class as an outline for your tests.

	"""		
	name = "Kite" # Name of the class to display
	def __init__(self):
		""" 
		Initialize all of your objects here.
		Be sure to call the Framework's initializer first.
		"""
		super(Masheet, self).__init__()

		#self.world.SetGravity(b2Vec2(0.0, 0.0))

		# Initialize all of the objects
		self.fluid = Air(velocity_20_mph)
		self.kite = Kite.MakeTestKite(self.fluid, self.world)
		print "%3.2f kg kite, air moving at %3.2fmph" % (self.kite.glider.body.GetMass(), mph(self.fluid.velocity.Length()))
		
		self.kite.step()

		self.setZoom(20)
		
	def Keyboard(self, key):
		"""
		The key is from pygame.locals.K_*
		(e.g., if key == K_z: ... )
		"""
		if key == pygame.K_a: self.kite.glider.rotate_wing(radians(1.0))
		elif key == pygame.K_s: self.kite.glider.rotate_wing(radians(-1.0))
		elif key == pygame.K_q: self.kite.move_anchor(0.01)
		elif key == pygame.K_w: self.kite.move_anchor(-0.01)
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

		# do stuff        
		self.kite.step()
		
		#if settings.draw:
		if True:
			self.DrawString(0,self.textLine,"Use a and s to rotate the main wing by 1 degree")
			self.textLine+=15
			absolute_v = mph(self.kite.glider.body.GetLinearVelocity().Length())
			relative_v = mph(self.kite.glider.velocity().Length())
			relative_v_wing = mph(self.kite.glider.wing.velocity().Length())
			force = reduce(add, [d[0] for d in self.kite.get_force_vectors()])
			self.DrawString(0,self.textLine, "Absolute velocity: %3.2f, Force: %3.2f,%3.2f" % (absolute_v, force.x, force.y))
			#self.DrawString(0,self.textLine,"Angle: %3.2f, Real Angle: %3.2f, Mass: %3.2f, Lift: %3.2f, Drag: %3.2f, Joint Force: %3.2f" %(degrees(self.wing_angle), 0, self.kite.glider.body.GetMass(), self.kite.glider.wing.lift.Length(), self.kite.glider.wing.drag.Length(), self.kite.anchorJoint.GetReactionForce().Length()))
			self.textLine+=15
			self.DrawString(0,self.textLine, "     V relative to wind: %3.f" % relative_v)
			self.textLine+=15
			self.DrawString(0,self.textLine, "Wing V relative to wind: %3.f" % relative_v_wing)
			self.textLine+=15
		
		super(Masheet, self).Step(settings)

		#if settings.draw:
		if True:
			for force in self.kite.get_force_vectors():
				world_force, world_point, color = force
				self.debugDraw.DrawSegment(world_point, world_point + (world_force / 100.0), color)
						
		self.kite.clear_force_vectors()


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

