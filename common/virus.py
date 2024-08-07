from common.actor import Actor
from common.globals import Globals
import pygame
class Virus(Actor):
    def __init__(self, x, y, mass, color):
        super().__init__(x, y, mass, color)
        self.split_mass = Globals.virus_split_mass

    def tick(self) -> None:
        self.check_colliding(Globals.cells)
        self.check_ejected(Globals.ejected)
        self.move()
    
    def tick_client(self) -> None:
        self.move()

    def check_colliding(self, cells):
        for cell in cells:
            if cell.can_consume(self):
                cell.consume_virus(self)

    def check_ejected(self, ejected):
        for e in ejected:
            if self.overlapping(e):
                if Globals.gamemode != 2:
                    self.consume(e)
                    if self.mass > self.split_mass:
                        self.split(e)
                else:
                    self.push(e)

    def push(self, e):
        self.xspeed += e.vector.x*50
        self.yspeed += e.vector.y*50
        Globals.objects_to_delete.add(e.id)

    def split(self, e):
        new_virus = Virus(self.x, self.y, Globals.virus_mass, self.color)
        new_virus.xspeed = e.vector.x*200
        new_virus.yspeed = e.vector.y*200
        Globals.viruses.append(new_virus)
        self.mass = Globals.virus_mass