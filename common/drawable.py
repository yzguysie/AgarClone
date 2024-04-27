import pygame
import math
from common.globals import Globals

class Drawable:
    def __init__(self, x, y, mass, color):

        self.x = x
        self.y = y
        self.xspeed = 0
        self.yspeed = 0
        self.mass = mass
        self.radius = math.sqrt(mass)
        self.smoothradius = self.radius
        self.color = color
        self.outline_color = (self.color[0]/1.5,self.color[1]/1.5, self.color[2]/1.5)
        self.outline_thickness = 3
        self.id = Globals.drawable_count
        Globals.drawable_count += 1
        self.consumer = False
        self.consumable = True


    def draw(self, window, camera, aa=True, outline=True):
             
        self.radius = math.sqrt(self.mass)
        self.outline_thickness = round(math.sqrt(self.smoothradius/Globals.camera.scale)/2)
        self.smoothradius += (self.radius - self.smoothradius)/15

        #Draw Outline
        if self.outline_thickness > 0 and outline:
            if aa:
                pygame.gfxdraw.aacircle(window, round(self.x/Globals.camera.scale-Globals.camera.x), round(self.y/Globals.camera.scale-Globals.camera.y), round(abs(self.smoothradius/Globals.camera.scale)), self.outline_color)
            pygame.gfxdraw.filled_circle(window, round(self.x/Globals.camera.scale-Globals.camera.x), round(self.y/Globals.camera.scale-Globals.camera.y), round(abs(self.smoothradius/Globals.camera.scale)), self.outline_color)
        
        #Draw Inside
        if aa:
            pygame.gfxdraw.aacircle(window, round(self.x/Globals.camera.scale-Globals.camera.x), round(self.y/Globals.camera.scale-Globals.camera.y), round(abs(self.smoothradius/Globals.camera.scale-self.outline_thickness)), self.color)
        pygame.gfxdraw.filled_circle(window, round(self.x/Globals.camera.scale-Globals.camera.x), round(self.y/Globals.camera.scale-Globals.camera.y), round(abs(self.smoothradius/Globals.camera.scale-self.outline_thickness)), self.color)


    def tick(self):
        self.check_consume()

    def distance_to(self, other, squared = False):
        if squared:
            return (self.x-other.x)**2+(self.y-other.y)**2
        return math.sqrt((self.x-other.x)**2+(self.y-other.y)**2)

    def touching(self, other):
        return math.pow((self.x-other.x), 2) + math.pow((self.y-other.y), 2) < math.pow((self.radius+other.radius), 2) 
    
    def overlapping(self, other):
        return (self.x-other.x)**2 + (self.y-other.y)**2 < (self.radius-other.radius/3)**2
    
    def can_consume(self, other):
        if other.consumable and other.id != self.id:
            if self.id not in Globals.objects_to_delete and other.id not in Globals.objects_to_delete:
                return self.mass > other.mass*1.3 and self.overlapping(other)
        return False

    def check_consume(self):
        global objects
        if self.consumer:
            for obj in Globals.all_drawable(agars_ = False):
                if self.can_consume(obj):
                    self.consume(obj)
         
    def consume(self, other):
        self.mass += other.mass
        Globals.objects_to_delete.add(other.id)
        