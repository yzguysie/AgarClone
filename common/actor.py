import pygame
import math
from common.globals import Globals

class Actor:
    s_next_actor_id: int = 0 # Used when deciding actor's ids
    SMOOTHNESS: float = 0.2 # Half-life in seconds of the difference between true radius and radius drawn. (Higher = Smoother, Lower = Snappier, more accurate)
    ELASTICITY: float = 0.5 # Proportion of momentum conserved after bouncing
    CONSUMER: bool
    CONSUMABLE: bool
    def __init__(self, x : float, y : float, mass : float, color: tuple):
        self.ID: int = Actor.s_next_actor_id
        Actor.s_next_actor_id += 1

        self.x: float = x
        self.y: float = y
        self.mass: float = mass
        self.color: tuple[int, int, int] = color

        self.xspeed: float = 0
        self.yspeed: float = 0

        self.radius: float = math.sqrt(mass)
        self.smoothradius: float = self.radius

        self.outline_color: tuple[int, int, int] = (self.color[0]/1.5, self.color[1]/1.5, self.color[2]/1.5)
        self.outline_thickness: int = 3

    
    def update_radius(self):
        self.radius = math.sqrt(self.mass)


    def draw(self, window, camera, aa=True, outline=True, sides: int = None) -> None:
        self.radius = math.sqrt(self.mass)
        self.outline_thickness = round(math.sqrt(self.smoothradius/Globals.camera.scale)/2)
        if not sides:

            self.smoothradius += (self.radius - self.smoothradius)/max(Globals.fps_*self.SMOOTHNESS, 1)
            #self.smoothradius = self.radius #FIXME only because server bugs smoothradius

            #Draw Outline
            if self.outline_thickness > 0 and outline:
                if aa:
                    pygame.gfxdraw.aacircle(window, camera.get_screen_x(self.x), camera.get_screen_y(self.y), round(abs(self.smoothradius/Globals.camera.scale)), self.outline_color)
                pygame.gfxdraw.filled_circle(window, camera.get_screen_x(self.x), camera.get_screen_y(self.y), round(abs(self.smoothradius/Globals.camera.scale)), self.outline_color)
            
            #Draw Inside
            if aa:
                pygame.gfxdraw.aacircle(window, camera.get_screen_x(self.x), camera.get_screen_y(self.y), round(abs(self.smoothradius/Globals.camera.scale-self.outline_thickness)), self.color)
            pygame.gfxdraw.filled_circle(window, camera.get_screen_x(self.x), camera.get_screen_y(self.y), round(abs(self.smoothradius/Globals.camera.scale-self.outline_thickness)), self.color)
        else:
            if sides < 3:
                raise Exception("Must be more than 2 sides in a polygon")
            points = []
            angle = -math.pi/sides

            x = camera.get_screen_x(self.x)
            y = camera.get_screen_y(self.y)
            if self.outline_thickness > 0 and outline:
                radius = self.radius/camera.scale
                for _ in range(sides):
                    angle += math.pi*2/sides
                    vector = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                    points.append((x+vector.x*radius, y+vector.y*radius))

                if aa:
                    pygame.gfxdraw.aapolygon(window, points, self.outline_color)
                pygame.gfxdraw.filled_polygon(window, points, self.outline_color)

            points = []
            angle = -math.pi/sides
            radius = self.radius/camera.scale-self.outline_thickness
            for _ in range(sides):
                angle += math.pi*2/sides
                vector = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                points.append((x+vector.x*radius, y+vector.y*radius))

            if aa:
                pygame.gfxdraw.aapolygon(window, points, self.color)
            pygame.gfxdraw.filled_polygon(window, points, self.color)


    def tick(self) -> None:
        self.move()
        self.update_radius()

    def tick_client(self) -> None:
        self.tick()

    def move(self) -> None:

        self.x += self.xspeed*Globals.gamespeed
        self.y += self.yspeed*Globals.gamespeed
        self.xspeed /= (1 + (4 * Globals.gamespeed))
        self.yspeed /= (1 + (4 * Globals.gamespeed))
        if abs(self.xspeed) < .01:
            self.xspeed = 0
        if abs(self.yspeed) < .01:
            self.yspeed = 0

        self.check_borders()

    def check_borders(self) -> None:
        if self.x > Globals.border_width:
            self.x = Globals.border_width
            self.xspeed *= -self.ELASTICITY
        if self.x < -Globals.border_width:
            self.x = -Globals.border_width
            self.xspeed *= -self.ELASTICITY

        if self.y > Globals.border_height:
            self.y = Globals.border_height
            self.yspeed *= -self.ELASTICITY
        if self.y < -Globals.border_height:
            self.y = -Globals.border_height
            self.yspeed *= -self.ELASTICITY

    def get_vector(self, pos: tuple = None, other: "Actor" = None, normalize = True) -> pygame.math.Vector2:
        if pos:
            x, y = pos
        elif other:
            x, y = other.x, other.y
        xdiff = x-self.x
        ydiff = y-self.y
        vector = pygame.math.Vector2(xdiff, ydiff)
        if normalize and abs(vector.x) > 0 and abs(vector.y) > 0:
            return vector.normalize()
        return vector

    def distance_to(self, other: "Actor", squared = False) -> float:
        if squared:
            return (self.x-other.x)**2+(self.y-other.y)**2
        return math.sqrt((self.x-other.x)**2+(self.y-other.y)**2)
    
    def touching(self, other: "Actor") -> bool:
        return math.pow((self.x-other.x), 2) + math.pow((self.y-other.y), 2) < math.pow((self.radius+other.radius), 2) 
    
    def overlapping(self, other: "Actor") -> bool:
        return math.pow(self.x-other.x, 2) + math.pow(self.y-other.y, 2) < math.pow(self.radius-other.radius/3, 2)
    
    def can_consume(self, other: "Actor") -> bool:
        if other.CONSUMABLE and other.ID != self.ID:
            if self.ID not in Globals.objects_to_delete and other.ID not in Globals.objects_to_delete:
                return self.mass > other.mass*1.3 and self.overlapping(other)
        return False

    def check_consume(self) -> None:
        global objects
        if self.CONSUMER:
            for obj in Globals.all_drawable(agars_ = False):
                if self.can_consume(obj):
                    self.consume(obj)

    def consume(self, other: "Actor") -> None:
        self.mass += other.mass
        Globals.objects_to_delete.add(other.ID)
