#!/usr/bin/env python
# encoding: utf-8
"""
craft.py

Created by Seth Nickell on 2008-10-18.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

from simutils import *
from fluid import Air, Water
from glider import Glider

class Craft(object):
	def __init__(self, windspeed, relative_scale, world):
		self.air = Air(b2Vec2(-windspeed, 0.0))
		self.water = Water(b2Vec2(0.0,0.0))
		self.world = world
		
		gap = 10.0
		
		h_length = 1.0
		h_wchord = 0.5
		h_wspan = 2.0
		h_schord = 0.25
		h_sspan = 0.75
		
		a_length = h_length * relative_scale
		a_wchord = h_wchord * relative_scale
		a_wspan = h_wspan * relative_scale
		a_schord = h_schord * relative_scale
		a_sspan = h_sspan * relative_scale
	
		self.airfoil   = Glider (x=0.0, y=gap*0.5, anchor_point=0.12, 
									polarity=1.0, body_length=a_length,
									wing_chord=a_wchord, wing_span=a_wspan, 
									stabilizer_chord=a_schord, stabilizer_span=a_sspan,
									fluid=self.air, box2dWorld=world, density=50.0)
	
		self.hydrofoil = Glider (x=0.0, y=gap*-0.5, anchor_point=0.12, 
									polarity=-1.0, body_length=h_length,
									wing_chord=h_wchord, wing_span=h_wspan, 
									stabilizer_chord=h_schord, stabilizer_span=h_sspan,
									fluid=self.water, box2dWorld=world, density=300.0)
		
		
		self.add_anchor_joint()
	
	def windspeed(self):
	    return self.air.velocity.Length()
	
	def move_anchor(self, glider, amount):
		glider.move_anchor(amount)
		if hasattr(self, "anchorJoint"): self.world.DestroyJoint(self.anchorJoint)
		self.add_anchor_joint()
	
	def add_anchor_joint(self):
		anchorJoint = b2DistanceJointDef()
		anchor1 = self.airfoil.get_anchor_point()
		anchor2 = self.hydrofoil.get_anchor_point()
		anchorJoint.Initialize(self.airfoil.body, self.hydrofoil.body, anchor1, anchor2);
		anchorJoint.collideConnected = True
		self.anchorJoint = self.world.CreateJoint(anchorJoint).getAsType()

	def get_center(self):
		return (self.airfoil.body.GetPosition() + self.hydrofoil.body.GetPosition()) * 0.5

	def step(self, damper=0.0):
		self.airfoil.step(damper)
		self.hydrofoil.step(damper)
		
	def draw(self, ctx):
		self.airfoil.draw(ctx)
		self.hydrofoil.draw(ctx)
		
	def get_force_vectors(self):
		forces = []
		forces += self.airfoil.get_force_vectors()		
		forces += self.hydrofoil.get_force_vectors()
		return forces

	def clear_force_vectors(self):
		self.airfoil.clear_force_vectors()
		self.hydrofoil.clear_force_vectors()

	def velocity(self):
		return (self.hydrofoil.velocity() + self.airfoil.velocity()) / 2.0

if __name__ == '__main__':
	main()

