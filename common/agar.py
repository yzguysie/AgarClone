from common.globals import Globals
from common.actor import Actor
import random

class Agar(Actor):

    def draw(self, window, camera):
        super().draw(window, camera, aa=True, outline=True)

    def tick(self):
        self.move()        
        if Globals.agar_grow:
            self.grow()

    def grow(self):
        if self.mass < Globals.agar_max_mass and random.randint(0, round(Globals.tickrate/Globals.agar_grow_speed)) == 1:
            self.mass += 1