#!/usr/bin/env python
# encoding: utf-8
"""
kite.py

Created by Seth Nickell on 2008-10-18.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

from simutils import *
from glider import Glider

class Kite(object):
	def __init__(self, x, y, anchor_point, polarity, body_length, wing_chord, wing_span, stabilizer_chord, stabilizer_span, fluid, box2dWorld):
		self.glider = Glider(x, y, anchor_point, polarity, body_length, wing_chord, wing_span, stabilizer_chord, stabilizer_span, fluid, box2dWorld)
		self.original_x = x
		
		# Make an anchor
		anchorBodyDef = b2BodyDef()
		anchorBodyDef.position.Set(x, 0.0)
		anchor = box2dWorld.CreateBody(anchorBodyDef)
		shapeDef = b2PolygonDef()
		shapeDef.SetAsBox(1.0, 1.0)
		shapeDef.density = 1000 # kg/m^3, from wikipedia for styrofoam density
		anchor.CreateShape(shapeDef)
		anchor.SetMassFromShapes()
		self.anchor = anchor
		self.world = box2dWorld
		
		# Create the anchor joint
		self.move_anchor(0.0)

	def MakeTestKite(fluid, world):		
		return Kite(x=2.0, y=20.0, anchor_point=0.12, polarity=1, body_length=6.0, 
						wing_chord=1, wing_span=4.0,
						stabilizer_chord=0.5, stabilizer_span=1.5,
						fluid=fluid, box2dWorld=world)

	def MakeGiantKite(fluid, world):		
		return Kite(x=2.0, y=20.0, anchor_point=0.12, polarity=1, body_length=8.0, 
						wing_chord=2, wing_span=12.0,
						stabilizer_chord=1, stabilizer_span=8.0,
						fluid=fluid, box2dWorld=world)

	MakeTestKite = staticmethod(MakeTestKite)
	MakeGiantKite = staticmethod(MakeGiantKite)		
	
	def get_force_vectors(self):
		return self.glider.get_force_vectors()

	def clear_force_vectors(self):
		self.glider.clear_force_vectors()
		
	def move_anchor(self, amount):
		anchor_point = self.glider.move_anchor(amount)
		if hasattr(self, "anchorJoint"): self.world.DestroyJoint(self.anchorJoint)
		self.add_anchor_joint(anchor_point)
			
	def add_anchor_joint(self, anchor_point):
		# Make a pully joint connecting the mount to the anchor
		anchorJoint = b2PulleyJointDef()
		anchor2 = self.anchor.GetWorldCenter()
		groundAnchor1 = b2Vec2(self.original_x - 0.2, 0.2)
		groundAnchor2 = b2Vec2(self.original_x - 0.1, 0.2)
		ratio = 1.0
		anchorJoint.Initialize(self.glider.body, self.anchor, groundAnchor1, groundAnchor2, anchor_point, anchor2, ratio);
		anchorJoint.maxLength2 = 10.0
		anchorJoint.collideConnected = False
		self.anchorJoint = self.world.CreateJoint(anchorJoint).getAsType()

	def step(self, damper=0.0):
		self.glider.step(damper)
		
	def draw(self, ctx):
		self.glider.draw(ctx)
