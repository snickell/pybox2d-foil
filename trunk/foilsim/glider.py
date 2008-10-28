#!/usr/bin/env python
# encoding: utf-8
"""
glider.py

Created by Seth Nickell on 2008-10-18.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

from simutils import *
from foil import Foil

class Glider(object):
	
	def __init__(self, x, y, anchor_point, polarity, body_length, wing_chord, wing_span, stabilizer_chord, stabilizer_span, fluid, box2dWorld, density=10.0):
		self.polarity = polarity
		self.body_length = body_length
		self.anchor_point = anchor_point
		
		# Make a body to Box2D for this foil
		bodyDef = b2BodyDef()
		bodyDef.position.Set(x, y)
		#bodyDef.linearDamping = 10.0
		#bodyDef.angularDamping = 1.0
		body = box2dWorld.CreateBody(bodyDef)
		shapeDef = b2PolygonDef()
		body_center = b2Vec2(-0.5 * body_length, 0.0)
		shapeDef.SetAsBox(body_length * 0.5, 0.05, body_center, 0)
		shapeDef.density = 0.0 # kg/m^3, from wikipedia for styrofoam density
		shapeDef.friction = 0.0
		body.CreateShape(shapeDef)
		
		print "Made body"

		self.wing = Foil(wing_chord, wing_span, fluid, 
							  body, b2Vec2(0.0, 0.15 * polarity), angle=radians(5) * polarity, density=density)
		print "Made wing"
		self.stabilizer = Foil(stabilizer_chord, stabilizer_span, fluid, 
								    body, b2Vec2(-body_length + stabilizer_chord, 0.15 * polarity), angle=0.0, density=density)
		print "Made stabilizer"
		body.SetMassFromShapes()
		
		self.body = body

	def get_force_vectors(self):
		forces = []
		forces += self.wing.appliedForces
		forces += self.stabilizer.appliedForces
		return forces
		
	def clear_force_vectors(self):
		self.wing.appliedForces = []
		self.stabilizer.appliedForces = []

	def rotate_wing(self, delta_angle):
		self.wing.set_angle(self.wing.get_angle() + (delta_angle * self.polarity))

	def set_wing_angle(self, new_angle):
		self.wing.set_angle(new_angle * self.polarity)
	
	def move_anchor(self, amount):
		self.anchor_point += amount
		return self.get_anchor_point()
		
	def get_anchor_point(self):
		return self.body.GetWorldPoint(b2Vec2(-self.body_length * self.anchor_point, 0.0))#-0.02 * self.body_length * self.polarity))
	
	def step(self, damper=0.0):
		if debug: print "Wing:"
		self.wing.step(damper)
		if debug: print "Stabilizer:"
		self.stabilizer.step(damper)
		pos = self.body.GetPosition()
		angle = self.body.GetAngle()
		if debug: print "X: %3.2f\tY: %3.2f\tA: %3.2f\tV(W): %4.2f\tL(W): %4.2f\tD(W): %4.2f\tV(S): %4.2f\tL(S): %4.2f\tD(S): %4.2f" % (pos.x, pos.y, degrees(angle), self.wing.velocity().Length(), self.wing.lift.Length(), self.wing.drag.Length(), self.stabilizer.velocity().Length(), self.stabilizer.lift.Length(), self.stabilizer.drag.Length())
		
	def draw(self, ctx):
		self.wing.draw(ctx)
		self.stabilizer.draw(ctx)
		
	def rotate(self, angle):
		rotation = self.body.GetAngle()
		position = self.body.GetPosition()
		self.body.SetXForm(position, rotation + angle)
		
	def velocity(self):
		return (self.wing.body.GetLinearVelocity() + self.stabilizer.body.GetLinearVelocity()) / 2.0
