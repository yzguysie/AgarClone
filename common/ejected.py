
from common.globals import Globals
from common.actor import Actor
import math
import pygame
import time
import random
class Ejected(Actor):

    def __init__(self, cell: Actor):
        super().__init__(cell.x, cell.y, Globals.ejected_size, cell.color)
       
        x, y = cell.target
        xdiff = x-cell.x
        ydiff = y-cell.y
        angle = math.atan2(ydiff, xdiff)+random.uniform(-.1, .1)
        self.vector = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        self.x = self.x+(cell.radius)*self.vector.x
        self.y = self.y+(cell.radius)*self.vector.y
        self.xspeed = self.vector.x*Globals.ejected_speed
        self.yspeed = self.vector.y*Globals.ejected_speed
        self.time_created = time.time()

    # def draw(self, window, camera):
    #     super().draw(window, camera, sides=10)

    def tick(self):
        self.move()
        if abs(self.xspeed)+abs(self.yspeed) > 0:
            self.vector = pygame.math.Vector2(self.xspeed, self.yspeed).normalize()

        self.check_colliding(Globals.cells)
        self.check_brown(Globals.brown_viruses)

        # Repel other Ejected
        for other in Globals.ejected:
            if other.id != self.id:
                if self.touching(other):
                    vector = other.get_vector(other = self)
                    velocity = ((self.radius+other.radius)-self.distance_to(other))*max(.5, Globals.gamespeed*5) # So they wont repel too much (looks kind of like soft-body)
                    self.x += vector.x*velocity/2
                    self.y += vector.y*velocity/2
                    other.x -= vector.x*velocity/2
                    other.y -= vector.y*velocity/2
        
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
            if virus.can_consume(self):
                virus.consume(self)