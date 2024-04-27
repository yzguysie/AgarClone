from common.drawable import Drawable
from common.globals import Globals

class Virus(Drawable):

    def __init__(self, x, y, mass, color):
        super().__init__(x, y, mass, color)

    def tick(self):
        self.check_colliding(Globals.cells)

    def check_colliding(self, cells):
        for thing in cells:
            if self.id not in Globals.objects_to_delete:
                if thing.mass >= Globals.virus_mass*1.3 and abs(self.x-thing.x)**2+abs(self.y-thing.y)**2 < (self.radius/4+thing.radius)**2:
                    thing.consume_virus(self)