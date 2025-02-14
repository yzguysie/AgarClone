from common.globals import Globals
from common.actor import Actor
import random

class Agar(Actor):
    CONSUMABLE = True
    CONSUMER = False
    def draw(self, window, camera):
        super().draw(window, camera, aa=True, outline=True)

    def tick(self) -> None:
        self.move()        
        if Globals.agar_grow:
            self.grow()
    
    def tick_client(self) -> None:
        self.move()
            
    def grow(self):
        if self.mass < Globals.agar_max_mass and random.randint(0, round(Globals.tickrate/Globals.agar_grow_speed)) == 1:
            self.mass += 1