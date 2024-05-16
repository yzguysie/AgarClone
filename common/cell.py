from common.actor import Actor
from common.globals import Globals
from common.ejected import Ejected
import time
import pygame
import math
class Cell(Actor):
   
    def __init__(self, x, y, mass, color, player):
        super().__init__(x, y, mass, color)
        self.consumer = True
        self.consumable = True
        self.extraxspeed = 0
        self.extrayspeed = 0
        self.slow_zone = 10
        self.speed = Globals.player_speed
        self.xspeed = 0
        self.yspeed = 0
        self.inertia = 5
        self.smoothradius = self.radius
        self.player = player
        self.target = player.target
        self.elasticity = 0 # Proportion of momentum conserved after bouncing


        self.time_created = time.time()

    def draw(self, window, camera):
        super().draw(window,camera)

        player_font_width = int(self.smoothradius/camera.scale/2+1)
        dialogue_font = pygame.font.SysFont(Globals.font, player_font_width)
        
        # Draw Player Name
        dialogue = dialogue_font.render(self.player.name, True, (255, 255, 255))
        dialogue_rect = dialogue.get_rect(center = (camera.get_screen_x(self.x), camera.get_screen_y(self.y)))
        window.blit(dialogue, dialogue_rect)

        # Draw cell mass
        dialogue = dialogue_font.render(str(round(self.mass)), True, (255, 255, 255))
        dialogue_rect = dialogue.get_rect(center = (camera.get_screen_x(self.x), camera.get_screen_y(self.y)+player_font_width))
        window.blit(dialogue, dialogue_rect)


    def move(self):
        # TODO - use drawable get_vector() method, but we need the velocity/distance, so wtf
        target_x, target_y = self.player.target
        xdiff = target_x-self.x
        ydiff = target_y-self.y

        # angle = math.atan2(ydiff, xdiff)
        vector = self.get_vector(pos = self.player.target)
        velocity = min(self.slow_zone, math.sqrt(xdiff**2 + ydiff**2))*10


        self.xspeed = vector.x*velocity*self.speed
        self.yspeed = vector.y*velocity*self.speed

        self.x += (self.xspeed+self.extraxspeed)/math.sqrt(self.radius)*Globals.gamespeed
        self.y += (self.yspeed+self.extrayspeed)/math.sqrt(self.radius)*Globals.gamespeed


        self.extraxspeed /= (1 + (2*Globals.gamespeed))
        self.extrayspeed /= (1 + (2*Globals.gamespeed))

        self.check_borders()

    def split(self, extra_speed = True):
        if len(self.player.cells) > Globals.player_max_cells or self.mass < Globals.player_split_min_mass:
            return None
        
        self.mass /= 2

        new_cell = Cell(self.x, self.y+.1, self.mass, self.color, self.player)
        new_cell.smoothradius = self.smoothradius # To make it look like the new cell is smoothly transitioning into being half the size
        
        Globals.cells.append(new_cell)
        self.player.cells.append(new_cell)

        if extra_speed:
            vector = self.get_vector(pos = self.player.target)
            new_cell.extraxspeed = vector.x*new_cell.radius**(2/3)*100
            new_cell.extrayspeed = vector.y*new_cell.radius**(2/3)*100

        return new_cell

    def tick(self) -> None:
        if self.mass > Globals.player_min_mass:
            self.decay(Globals.player_decay_rate)
        if self.mass > Globals.player_max_cell_mass:
            self.split()
        self.move()
        self.check_colliding(Globals.cells)
        self.check_viruses(Globals.brown_viruses)
        self.check_agars(Globals.agars)
       
    def decay(self, rate) -> None:
        self.mass -= self.mass*rate*Globals.gamespeed


    def check_agars(self, agars) -> None:
        for agar in agars:
            if self.can_consume(agar):
                self.consume(agar)

    def consume_virus(self, virus: Actor) -> None:
        self.mass += virus.mass
        Globals.objects_to_delete.add(virus.id)
        cells_affected = [self]
        for _ in range(16):
            for cell in cells_affected:
                if len(self.player.cells) < Globals.player_max_cells and cell.mass > Globals.player_split_min_mass:
                    cells_affected.append(cell.split(extra_speed = False))

    # def consume_brown_virus(self, virus: Actor) -> None:
    #     self.mass += virus.mass
    #     Globals.objects_to_delete.add(virus.id)
    #     cells_affected = [self]
    #     for _ in range(16):
    #         for cell in cells_affected:
    #             if len(self.player.cells) < Globals.player_max_cells and cell.mass > Globals.player_split_min_mass:
    #                 cells_affected.append(cell.split(extra_speed = False))

    def check_viruses(self, viruses) -> None:
        for virus in viruses:
            if self.can_consume(virus):
                self.consume_virus(virus)
            elif virus.can_consume(self):
                virus.consume(self)
       
    def eject_mass(self) -> None:
        e = Ejected(self)
        self.mass -= Globals.ejected_loss
        self.radius = math.sqrt(self.mass)
        Globals.ejected.append(e)

    def check_colliding(self, cells: list["Cell"]):
        for other in self.player.cells:
            if other.id != self.id:
                if self.touching(other):
                    # If cells are too young, repel each other
                    if (time.time()-other.time_created < Globals.player_recombine_time*(self.mass**(1/4)/4) or time.time()-self.time_created < Globals.player_recombine_time*(self.mass**(1/4)/4)) and other.player == self.player:
                        if time.time()-other.time_created > .25 and time.time()-self.time_created > .25: # "Buffer" so that cells don't instantly repel each other, makes splitting smoother
                            max_dist = (self.radius + other.radius)-self.distance_to(other) # Ideal distance to move cells so they are touching each other but not overlapping (Don't want to repel more than this)
                            move_speed = 3500*Globals.gamespeed # Maximum amount cells can repel each other in one game tick
                            vector = other.get_vector(other = self)
                            velocity = min(max_dist, move_speed*Globals.gamespeed) # cells will never become too far apart, and not too quickly
                            
                            combined_mass = self.mass+other.mass
                            self.x += vector.x*velocity*(other.mass/combined_mass)
                            self.y += vector.y*velocity*(other.mass/combined_mass)
                            other.x -= vector.x*velocity*(self.mass/combined_mass)
                            other.y -= vector.y*velocity*(self.mass/combined_mass)

                    # If cells are old enough, recombine
                    else:
                        if self.overlapping(other):
                            if self.id not in Globals.objects_to_delete and other.id not in Globals.objects_to_delete:
                                self.consume(other)

        for other in cells:
            if other.player != self.player:
                if self.can_consume(other):
                    self.consume(other)
                elif other.can_consume(self):
                    other.consume(self)