from common.globals import Globals
from common.drawable import Drawable
import random

class Agar(Drawable):

    def __init__(self, x, y, mass, color):
        super().__init__(x, y, mass, color)

    def draw(self, window, camera):
        super().draw(window, camera, True, True)


    def tick(self):
        self.check_colliding(Globals.cells)
        self.x += self.xspeed
        self.y += self.yspeed
        self.xspeed /= 1+(12/Globals.tickrate)
        self.yspeed /= 1+(12/Globals.tickrate)
        if abs(self.xspeed) < .01:
            self.xspeed = 0
        if abs(self.yspeed) < .01:
            self.yspeed = 0

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
        
        if Globals.agar_grow:
            if self.mass < Globals.agar_max_mass and random.randint(0, round(Globals.tickrate/Globals.agar_grow_speed)) == 1:
                self.grow()

    def grow(self):
        self.mass += 1


    def check_colliding(self, cells):
        for thing in cells:
            if thing.can_consume(self):
                thing.consume(self)