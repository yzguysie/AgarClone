
from common.globals import Globals
from common.drawable import Drawable
import random
import pygame
import math
from common.agar import Agar
class BrownVirus(Drawable):
    def __init__(self, x, y, mass, color):
        super().__init__(x, y, mass, color)
        self.consumer = True
        self.spit_rate = 120
        self.startmass = mass
        self.smoothradius = self.radius

    def tick(self):
        spit_rate = 120
        if Globals.tickrate < spit_rate:
            for i in range(round(spit_rate/Globals.tickrate)):
                if self.mass > self.startmass:
                    self.spit()
        else:
            if (Globals.frames%(round(Globals.tickrate/spit_rate)) == 0):
                if self.mass > self.startmass:
                    self.spit()
        
        if random.randint(0, Globals.tickrate) == 0 and len(Globals.agars) < Globals.max_agars:
            self.spit() 

        self.check_consume()
            

    def spit(self):
        spit_mult = 1
        spit_mass = 1
        spit_speed = random.uniform(.8, 1)
        rand_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        angle = random.uniform(0, 360)
        vector = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        spatted_x = self.x+(self.radius-math.sqrt(spit_mass))*vector[0]
        spatted_y = self.y+(self.radius-math.sqrt(spit_mass))*vector[1]
        spatted = Agar(spatted_x, spatted_y, spit_mass, rand_color)
        spatted.xspeed = vector[0]*spit_speed
        spatted.yspeed = vector[1]*spit_speed
        Globals.agars.add(spatted)
        self.mass -= spatted.mass/spit_mult
        self.mass = max(self.mass, self.startmass)
       

       

    def colliding(self, thing):
        return abs(self.x-thing.x)**2+abs(self.y-thing.y)**2 < (self.radius/4+thing.radius)**2