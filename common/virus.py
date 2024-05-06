from common.drawable import Drawable
from common.globals import Globals

class Virus(Drawable):

    def __init__(self, x, y, mass, color):
        super().__init__(x, y, mass, color)
        self.split_mass = Globals.virus_split_mass

    def tick(self):
        self.check_colliding(Globals.cells)
        self.check_ejected(Globals.ejected)
        self.x += self.xspeed
        self.y += self.yspeed
        self.xspeed /= (1 + (12/Globals.tickrate))
        self.yspeed /= (1 + (12/Globals.tickrate))

    def check_colliding(self, cells):
        for cell in cells:
            if cell.can_consume(self):
                cell.consume_virus(self)

    def split(self, e):
        new_virus = Virus(self.x, self.y, Globals.virus_mass, self.color)
        new_virus.xspeed = e.vector[0]*500/Globals.tickrate
        new_virus.yspeed = e.vector[1]*500/Globals.tickrate
        Globals.viruses.append(new_virus)
        self.mass = Globals.virus_mass




    def check_ejected(self, ejected):
        for e in ejected:
            if self.overlapping(e):
                self.consume(e)
                if self.mass > self.split_mass:
                    self.split(e)


