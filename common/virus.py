from common.drawable import Drawable
from common.globals import Globals

class Virus(Drawable):

    def __init__(self, x, y, mass, color):
        super().__init__(x, y, mass, color)
        self.split_mass = 200

    def tick(self):
        self.check_colliding(Globals.cells)
        self.check_ejected(Globals.ejected)
        self.x += self.xspeed
        self.y += self.yspeed
        self.xspeed /= (1 + (12/Globals.fps))
        self.yspeed /= (1 + (12/Globals.fps))

    def check_colliding(self, cells):
        for cell in cells:
            if self.id not in Globals.objects_to_delete:
                if cell.mass >= Globals.virus_mass*1.3 and abs(self.x-cell.x)**2+abs(self.y-cell.y)**2 < (self.radius/4+cell.radius)**2:
                    cell.consume_virus(self)

    def split(self, e):
        new_virus = Virus(self.x, self.y, Globals.virus_mass, self.color)
        new_virus.xspeed = e.vector[0]*500/Globals.fps
        new_virus.yspeed = e.vector[1]*500/Globals.fps
        Globals.viruses.append(new_virus)
        self.mass = Globals.virus_mass




    def check_ejected(self, ejected):
        for e in ejected:
            if self.overlapping(e):
                self.consume(e)
                if self.mass > self.split_mass:
                    self.split(e)


