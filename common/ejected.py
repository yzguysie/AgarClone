
from common.globals import Globals
from common.drawable import Drawable
import math
import pygame
import time
import random
class Ejected(Drawable):

    def __init__(self, cell):
        super().__init__(cell.x, cell.y, Globals.ejected_size, cell.color)
       
        x, y = cell.target
        xdiff = x-cell.x
        ydiff = y-cell.y
        angle = math.atan2(ydiff, xdiff)+random.uniform(-.1, .1)
        self.vector = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        self.x = self.x+(cell.radius)*self.vector[0]
        self.y = self.y+(cell.radius)*self.vector[1]
        self.xspeed = self.vector[0]*Globals.ejected_speed*60
        self.yspeed = self.vector[1]*Globals.ejected_speed*60
        self.time_created = time.time()

    def tick(self):
        global ejected_to_calculate
        self.radius = math.sqrt(self.mass)
        self.smoothradius += (self.radius - self.smoothradius)/15
        global ejected_size
        self.x += self.xspeed/Globals.tickrate
        self.y += self.yspeed/Globals.tickrate

        self.xspeed /= 1+(6/Globals.tickrate)
        self.yspeed /= 1+(6/Globals.tickrate)


        if self.x > Globals.border_width:
            self.x = Globals.border_width
            self.xspeed *= -.5
        if self.x < -Globals.border_width:
            self.x = -Globals.border_width
            self.xspeed *= -.5
        if self.y > Globals.border_height:
            self.y = Globals.border_height
            self.yspeed *= -.5
        if self.y < -Globals.border_height:
            self.y = -Globals.border_height
            self.yspeed *= -.5
           
       
        



        self.check_colliding(Globals.cells)
        self.check_brown(Globals.brown_viruses)

        # Repel other Ejected
        for other in Globals.ejected:
            if other.id != self.id:
                if self.touching(other):
                    # try:
                    #     xdiff = self.x-other.x
                    #     ydiff = self.y-other.y
                    #     distance_squared = xdiff**2+ydiff**2
                    #     xforce = xdiff/distance_squared*50
                    #     yforce = ydiff/distance_squared*50
                    #     self.x += xforce/Globals.fps
                    #     self.y += yforce/Globals.fps
                    #     other.x -= xforce/Globals.fps
                    #     other.y -= yforce/Globals.fps
                    # except Exception as e: print(e + " At ejected collision")
                    if self.touching(other):
                        xdiff = self.x-other.x
                        ydiff = self.y-other.y
                        angle = math.atan2(ydiff, xdiff)
                        vector = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                        velocity = ((self.radius+other.radius)-self.distance_to(other))*Globals.gamespeed # So they wont repel too much (looks kind of like soft-body)
                        self.x += vector[0]*velocity/2
                        self.y += vector[1]*velocity/2
                        other.x -= vector[0]*velocity/2
                        other.y -= vector[1]*velocity/2
        
        # Consume other ejected

        # for mass in ejected:
        #         if mass.x != self.x and mass.y != self.y:
        #                 if ((self.x-mass.x)**2+(self.y-mass.y)**2) < (self.radius/2+mass.radius/2)**2 and mass.id not in objects_to_delete and self.id not in objects_to_delete and self.mass >= mass.mass:
        #                         self.consume(mass)


    def check_colliding(self, cells):
        #if time.time() - self.time_created >= 0.3:
        for thing in cells:
            if thing.can_consume(self):
                thing.consume(self)


    def check_brown(self, brown_viruses):
        for virus in brown_viruses:
            if self.id not in Globals.objects_to_delete:
                if (self.x-virus.x)**2+(self.y-virus.y)**2 < (virus.radius)**2:
                    virus.consume(self)