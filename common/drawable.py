import pygame
import math
from common.globals import Globals

class Drawable:
    def __init__(self, x : float, y : float, mass : float, color: tuple):

        self.x = x
        self.y = y
        self.xspeed = 0
        self.yspeed = 0
        self.mass = mass
        self.radius = math.sqrt(mass)
        self.smoothradius = self.radius
        self.smoothness = .25 # Half life in seconds of the difference between true radius and radius drawn. (Higher = Smoother, Lower = Snappier, more accurate)
        self.color = color
        self.outline_color = (self.color[0]/1.5,self.color[1]/1.5, self.color[2]/1.5)
        self.outline_thickness = 3
        self.id = Globals.drawable_count
        Globals.drawable_count += 1
        self.consumer = False
        self.consumable = True
        self.elasticity = .5 # Proportion of momentum conserved after bouncing

    def draw(self, window, camera, aa=True, outline=True) -> None:
             
        self.radius = math.sqrt(self.mass)
        self.outline_thickness = round(math.sqrt(self.smoothradius/Globals.camera.scale)/2)
        self.smoothradius += (self.radius - self.smoothradius)/max(Globals.fps_*self.smoothness, 1)

        #Draw Outline
        if self.outline_thickness > 0 and outline:
            if aa:
                pygame.gfxdraw.aacircle(window, camera.get_screen_x(self.x), camera.get_screen_y(self.y), round(abs(self.smoothradius/Globals.camera.scale)), self.outline_color)
            pygame.gfxdraw.filled_circle(window, camera.get_screen_x(self.x), camera.get_screen_y(self.y), round(abs(self.smoothradius/Globals.camera.scale)), self.outline_color)
        
        #Draw Inside
        if aa:
            pygame.gfxdraw.aacircle(window, camera.get_screen_x(self.x), camera.get_screen_y(self.y), round(abs(self.smoothradius/Globals.camera.scale-self.outline_thickness)), self.color)
        pygame.gfxdraw.filled_circle(window, camera.get_screen_x(self.x), camera.get_screen_y(self.y), round(abs(self.smoothradius/Globals.camera.scale-self.outline_thickness)), self.color)


    def tick(self) -> None:
        self.move()
        self.check_borders()
        self.check_consume()
        

    def move(self) -> None:
        self.x += self.xspeed
        self.y += self.yspeed
        self.xspeed /= (1 + (12/Globals.tickrate))
        self.yspeed /= (1 + (12/Globals.tickrate)) 

    def check_borders(self) -> None:
        if self.x > Globals.border_width:
            self.x = Globals.border_width
            self.xspeed *= -self.elasticity
        if self.x < -Globals.border_width:
            self.x = -Globals.border_width
            self.xspeed *= -self.elasticity

        if self.y > Globals.border_height:
            self.y = Globals.border_height
            self.yspeed *= -self.elasticity
        if self.y < -Globals.border_height:
            self.y = -Globals.border_height
            self.yspeed *= -self.elasticity

    def get_vector(self, pos: tuple = None, other: "Drawable" = None, normalize = True) -> pygame.math.Vector2:
        if pos:
            x, y = pos
        elif other:
            x, y = other.x, other.y
        xdiff = x-self.x
        ydiff = y-self.y
        if normalize:
            return pygame.math.Vector2(xdiff, ydiff).normalize()
        return pygame.math.Vector2(xdiff, ydiff)

    def distance_to(self, other: "Drawable", squared = False) -> float:
        if squared:
            return (self.x-other.x)**2+(self.y-other.y)**2
        return math.sqrt((self.x-other.x)**2+(self.y-other.y)**2)
    
    def touching(self, other: "Drawable") -> bool:
        return math.pow((self.x-other.x), 2) + math.pow((self.y-other.y), 2) < math.pow((self.radius+other.radius), 2) 
    
    def overlapping(self, other: "Drawable") -> bool:
        return math.pow(self.x-other.x, 2) + math.pow(self.y-other.y, 2) < math.pow(self.radius-other.radius/3, 2)
    
    def can_consume(self, other: "Drawable") -> bool:
        if other.consumable and other.id != self.id:
            if self.id not in Globals.objects_to_delete and other.id not in Globals.objects_to_delete:
                return self.mass > other.mass*1.3 and self.overlapping(other)
        return False

    def check_consume(self) -> None:
        global objects
        if self.consumer:
            for obj in Globals.all_drawable(agars_ = False):
                if self.can_consume(obj):
                    self.consume(obj)

    def consume(self, other: "Drawable") -> None:
        self.mass += other.mass
        Globals.objects_to_delete.add(other.id)
