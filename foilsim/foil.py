#!/usr/bin/env python
# encoding: utf-8
"""
foil.py

Created by Seth Nickell on 2008-10-18.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

from simutils import *
import foil_model

class Foil(object):		
	def __init__(self, chord, span, fluid, body, leading_edge_position, angle, density):
		self.oswalds_efficiency = 0.90 # for naca 0015
		self.cd_min = 0.0074 # for naca 0015
		self.chord = float(chord)
		self.span = float(span)
		self.fluid = fluid
		self.area = float(chord) * float(span)
		self.aspect_ratio = float(span) / float(chord)
		self.leading_edge_position = leading_edge_position
		self.angle_offset = angle
		self.density = density
		
		self.appliedForces = []
		
		self.use_table = True
		self.reynolds = 1000000
		self.cd_table = foil_model.cd
		self.cl_table = foil_model.cl
		
		if body != None:
			self.body = body			
			self.add_shape_to_body(angle)


	def step(self, damper=0.0):
		lift, drag, angle_of_attack = self.calculate_lift_drag_vectors()
		
		lift -= lift * damper
		drag -= drag * damper
		
		# Call ApplyForce using the returned vectors, and record them for debug drawing
		self.appliedForces = []
		self._apply_force(lift, self._aerodynamic_center_world(), b2Color(0.0, 1.0, 0.0))
		self._apply_force(drag, self._aerodynamic_center_world(), b2Color(1.0, 0.0, 0.0))
		
		self.lift = lift
		self.drag = drag
		self.angle_of_attack = angle_of_attack

		#print "%3.1f°\tlift: (%3.1f, %3.1f)\tdrag: (%3.1f, %3.1f)\tL/D: %3.1f" % (degrees(angle_of_attack), lift.x, lift.y, drag.x, drag.y, lift.Length() / drag.Length())


	def calculate_lift_drag_vectors(self):
		# Calculate the velocity of the foil relative to the fluid its suspended in
		relative_velocity = self.velocity()
		velocity_squared = relative_velocity.LengthSquared()
		
		foil_angle = self.body.GetAngle() + self.angle_offset
		flow_angle = math.atan2(relative_velocity.y, relative_velocity.x)
		angle_of_attack = foil_angle - flow_angle
		if debug: print "\tFoil angle is %3.2f" % degrees(foil_angle)
		lift_magnitude, drag_magnitude, angle_of_attack, s, r = self.calculate_lift_drag_magnitude(angle_of_attack, velocity_squared)
				
		# Convert the magnitudes into vectors, drag in the direction of fluid flow, lift clockwise normal
		flow_unit_vector = relative_velocity.copy() * -1.0
		flow_unit_vector.Normalize()
		lift_vector = b2Vec2(flow_unit_vector.y, -flow_unit_vector.x) * lift_magnitude
		drag_vector = flow_unit_vector * drag_magnitude
		
		#if relative_velocity > self.fluid.velocity * 2.0:
		#	print "CLAMP"
		#	lift_vector += self.lift / 2.0
		#	drag_vector += self.drag / 2.0
		
		if debug: print "\tLift vector is: %s" % (str(lift_vector))
		if debug: print "\tDrag vector is: %s" % (str(drag_vector))
		
		return (lift_vector, drag_vector, angle_of_attack)


	def calculate_lift_drag_magnitude(self, angle, velocity_squared):
		angle_of_attack, reverse_flow = self.simplify_angle(angle)
		
		# We call the wing stalled if the angle is greater than 10 degrees
		stalled = abs(angle_of_attack) > radians(10.0) or reverse_flow
		
		# Calculate coefficients of lift/drag using thin airfoil theory
		cl = self._coefficient_of_lift(angle_of_attack)
		cd = self._coefficient_of_drag(cl, angle_of_attack)
		
		if not self.use_table:
			if stalled: cl = 1.0 if angle_of_attack >= 0 else -1.0
			if reverse_flow: cl *= -1.0
				
		lift_magnitude = 0.5 * self.fluid.density * velocity_squared * self.area * cl
		drag_magnitude = 0.5 * self.fluid.density * velocity_squared * self.area * cd
			
		return (lift_magnitude, drag_magnitude, angle_of_attack, stalled, reverse_flow)

	def _coefficient_of_lift(self, angle_of_attack):
		if self.use_table: return self.cl_table.get_coefficient(angle_of_attack, self.reynolds)
		else: return 2.0 * math.pi * angle_of_attack
	
	def _coefficient_of_drag(self, cl, angle_of_attack):
		if self.use_table: return self.cd_table.get_coefficient(angle_of_attack, self.reynolds)
		else: return self.cd_min + (cl * cl) / (math.pi * self.aspect_ratio * self.oswalds_efficiency)
		
	def get_angle(self):
		return self.angle_offset
	
	def set_angle(self, new_angle):
		self.angle_offset = new_angle
		self.body.DestroyShape(self.shape)
		self.add_shape_to_body(new_angle)
		
	def add_shape_to_body(self, angle):
		shapeDef = b2PolygonDef()
		thickness = self.chord * 0.08
		foil_center = self.leading_edge_position - b2Vec2(0.5 * self.chord, 0.0)
		if thickness < 0.1:
			thickness = 0.1
			print "WARNING: setting shape thickness of foil to min to make Box2D happy"
		print "Adding shape with chord %3.2f, thickness %3.2f, location %s" % (self.chord, thickness, str(foil_center))
		shapeDef.SetAsBox(self.chord * 0.5, thickness * 0.5, foil_center, angle)
		shapeDef.density = self.density
		shapeDef.friction = 0.0
		self.shape = self.body.CreateShape(shapeDef)
		
		aeroShapeDef = b2CircleDef()
		aeroShapeDef.radius = 0.15
		aeroShapeDef.density = 0.0
		center = self._aerodynamic_center()
		aeroShapeDef.localPosition.Set(center.x, center.y)
		self.body.CreateShape(aeroShapeDef)

	# Map an angle to -180 to 180
	def simplify_angle(self, input_angle):
		angle = degrees(input_angle)
		
		# Get rid of angles above 360
		angle %= 360.0
		
		reverse_flow = False
		if 0.0 <= angle <= 90.0:
			pass
		elif 90.0 < angle <= 180.0:
			reverse_flow = True
			angle = 180.0 - angle
		elif 180.0 < angle < 270.0:
			reverse_flow = True
			angle = 180.0 - angle
		elif 270.0 <= angle <= 360.0:
			angle += -360.0
			
		return (radians(angle), reverse_flow)
	
	def linear_velocity_from_angular(self, position, cm, angular_velocity):
		vector_from_cm = position - cm
		linear_velocity_magnitude =  vector_from_cm.Length() * angular_velocity
		vector_from_cm.Normalize()
		return b2Vec2(-vector_from_cm.y, vector_from_cm.x) * linear_velocity_magnitude

	# Calculate velocity of the foil, including the instantaneous angular component
	def velocity(self):
		instantaneous_angular_velocity = self.linear_velocity_from_angular(position=self._aerodynamic_center(), cm=self.body.GetLocalCenter(), angular_velocity=self.body.GetAngularVelocity())
		relative_velocity = self.body.GetLinearVelocity() + instantaneous_angular_velocity - self.fluid.velocity
		if debug: print "Velocity is %s" % (relative_velocity)
		return relative_velocity
		
	def _apply_force(self, world_force, world_point, color):	
		self.appliedForces.append((world_force, world_point, color))
		self.body.ApplyForce(world_force, world_point)
	
	# Aerodynamic center is 1/4 of chord length back
	def _aerodynamic_center(self):
		return self.leading_edge_position - b2Vec2(self.chord * 0.25, 0.0)
		
	def _aerodynamic_center_world(self):
		return self.body.GetWorldPoint(self._aerodynamic_center())
		
	
	# Code for generating aerodynamic lift/drag tables
	def Table():
		from fluid import Air		
		air = Air(b2Vec2(0.0, 0.0))
		location = b2Vec2(0.0, 0.0)
		foil = Foil(chord=0.5, span=3.0, fluid=air, body=None, leading_edge_position=location, angle=0.0, density=0.0)
		foil.table()
		return foil
	Table = staticmethod(Table)
		
	def table(self):
		v2 = 8.94 * 8.94
		print "Angle\tL\tD\tL/D\tCL\tCD"
		for angle_of_attack in range(0,361):
			l, d, a, s, r = self.calculate_lift_drag_magnitude(radians(angle_of_attack), v2)
			cl = self._coefficient_of_lift(a)
			cd = self._coefficient_of_drag(cl, a)
			print "%d°\t%6.1f\t%6.1f\t%4.3f\t%6.2f\t%6.2f" % (angle_of_attack, l * 0.224808943, d * 0.224808943, l / d, cl, cd)

	def draw(self, ctx):
		position = self.body.GetPosition()
		angle = self.body.GetAngle()
		center = self._aerodynamic_center()
		thickness = 0.10 * self.chord
		
		ctx.save()
		
		#print "Drawing at %3.1f, %3.1f  (angle=%3.1f)" % (position.x, position.y, degrees(angle))
		ctx.translate(position.x, position.y)
		ctx.rotate(angle)
		
		# Draw the center of lift
		ctx.set_line_width(0.025)
		ctx.arc(0, 0, thickness, 0, 2.0 * math.pi)
		ctx.set_source_rgb(0, 0, 1)
		ctx.fill_preserve()
		ctx.set_source_rgb(0, 0, 0)
		ctx.stroke()
		
		# Draw the lift vector
		ctx.save()
		ctx.scale(0.05, 0.05)
		ctx.set_source_rgb(0, 0, 1)
		ctx.set_line_width(0.5)
		ctx.move_to(0,0)
		ctx.line_to(self.lift.x, self.lift.y)
		ctx.stroke()
		ctx.set_source_rgb(0,1,0)
		ctx.move_to(0, 0)
		ctx.line_to(self.drag.x, self.drag.y)
		ctx.stroke()
		ctx.restore()
			
		# Draw the foil
		ctx.translate(-center.x, center.y)
		ctx.set_line_width(0.025)
		ctx.set_source_rgb(1,0,0)
		ctx.move_to(0, thickness)
		ctx.line_to(0, -thickness)
		ctx.line_to(-self.chord, 0)
		ctx.close_path()
		
		ctx.stroke()
		
		ctx.restore()
	
if __name__ == '__main__':
	Foil.Table()

