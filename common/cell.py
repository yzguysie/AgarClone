from common.drawable import Drawable
from common.globals import Globals
from common.ejected import Ejected
import time
import pygame
import math
class Cell(Drawable):
   
    def __init__(self, x, y, mass, color, player):
        super().__init__(x, y, mass, color)
        self.consumer = True
        self.consumable = True
        self.extraxspeed = 0
        self.extrayspeed = 0
        self.slow_zone = 10
        self.speed = 1
        self.xspeed = 0
        self.yspeed = 0
        self.inertia = 5
        self.smoothradius = self.radius
        self.player = player
        self.target = player.target


        self.time_created = time.time()

    def draw(self, window, camera):
        super().draw(window,camera)

        # player_font_width = int(self.radius/camera.scale/2+1)
        # dialogue_font = pygame.font.SysFont(font, player_font_width)
        
        # # Draw Player Name
        # dialogue = dialogue_font.render(self.player.mode, aa_text, Colors.white)
        # dialogue_rect = dialogue.get_rect(center = (round(self.x/camera.scale-camera.x), round(self.y/camera.scale-camera.y)))
        # window.blit(dialogue, dialogue_rect)

        # # Draw cell mass
        # dialogue = dialogue_font.render(str(int(self.mass)), aa_text, Colors.white)
        # dialogue_rect = dialogue.get_rect(center = (round(self.x/camera.scale-camera.x), round(self.y/camera.scale-camera.y+player_font_width)))
        # window.blit(dialogue, dialogue_rect)


    def move(self):
        target_x, target_y = self.player.target
        xdiff = target_x-self.x
        ydiff = target_y-self.y

        angle = math.atan2(ydiff, xdiff)
        vector = pygame.math.Vector2(math.cos(angle), math.sin(angle))

        velocity = min(self.slow_zone, math.sqrt(xdiff**2+ydiff**2))*10

        #         x, y = pygame.mouse.get_pos()
        #         xdiff = x-int(self.x/scale-camera_x+.5)
        #         ydiff = y-int(self.y/scale-camera_y+.5)
        #         angle = math.atan2(ydiff, xdiff)
        #         vector = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        #         velocity = min(self.slow_zone, math.sqrt(xdiff**2+ydiff**2))




        # if fps_ < fps/smooth_fix_limit or fps_ > fps*smooth_fix_limit:
        #     self.xspeed = velocity*vector[0]*self.speed/fps*smooth_fix_limit
        #     self.yspeed = velocity*vector[1]*self.speed/fps*smooth_fix_limit

        # else:
        #     self.xspeed = velocity*vector[0]*self.speed/fps_
        #     self.yspeed = velocity*vector[1]*self.speed/fps_
        self.xspeed = velocity*vector[0]*self.speed*Globals.gamespeed
        self.yspeed = velocity*vector[1]*self.speed*Globals.gamespeed

        self.x += (self.xspeed+self.extraxspeed)/math.sqrt(self.radius)
        self.y += (self.yspeed+self.extrayspeed)/math.sqrt(self.radius)

        if self.x > Globals.border_width:
            self.x = Globals.border_width
        if self.x < -Globals.border_width:
            self.x = -Globals.border_width

        if self.y > Globals.border_height:
            self.y = Globals.border_height
        if self.y < -Globals.border_height:
            self.y = -Globals.border_height

        self.extraxspeed /= 1.05
        self.extrayspeed /= 1.05

    def split(self):
        
        if len(self.player.cells) > Globals.player_max_cells or self.mass < Globals.player_split_min_mass:
                return
        
        self.mass /= 2
        new_cell = Cell(self.x, self.y+.1, self.mass, self.color, self.player)
        Globals.cells.append(new_cell)
        self.player.cells.append(new_cell)
        

        extrax = (self.xspeed)*Globals.gamespeed*100
        extray = (self.yspeed)*Globals.gamespeed*100



       
       
        total_speed = math.sqrt(extrax**2+extray**2)
       
        if extrax**2+extray**2 > Globals.player_speed**2*2:
                percent_x = extrax/total_speed
                percent_y = extray/total_speed

               
                       
               
                extrax = Globals.player_speed*percent_x*2
                extray = Globals.player_speed*percent_y*2

        Globals.cells[len(Globals.cells)-1].extraxspeed = extrax*Globals.cells[len(Globals.cells)-1].radius**(2/3)
        Globals.cells[len(Globals.cells)-1].extrayspeed = extray*Globals.cells[len(Globals.cells)-1].radius**(2/3)


    def tick(self):
        self.apply_physics()
       
    def apply_physics(self):
        if self.mass > Globals.player_min_mass:
            if Globals.fps_ < Globals.fps/Globals.smooth_fix_limit or Globals.fps_ > Globals.fps*Globals.smooth_fix_limit:
                self.mass -= self.mass*Globals.player_decay_rate*Globals.gamespeed
            else:
                self.mass -= self.mass*Globals.player_decay_rate*Globals.gamespeed
        self.move()
        self.check_colliding(Globals.cells)
        self.check_viruses(Globals.brown_viruses)



    def consume_virus(self, virus):
        self.mass += virus.mass
        Globals.objects_to_delete.add(virus.id)
        while len(self.player.cells) < Globals.player_max_cells and self.mass > Globals.player_split_min_mass:
                self.split()


    def consume_brown_virus(self, virus):
        self.mass += virus.mass
        Globals.objects_to_delete.add(virus.id)
        while len(self.player.cells) < Globals.player_max_cells and self.mass > Globals.player_split_min_mass:
                self.split()  
               
   

    def check_viruses(self, viruses):
        for virus in viruses:
            if self.mass*1.3 < virus.mass:
                if (virus.x-self.x)**2+(virus.y-self.y)**2 < (virus.radius-self.radius/3)**2:
                    if self.id not in Globals.objects_to_delete and virus.id not in Globals.objects_to_delete:
                        virus.consume(self)
            if self.mass > virus.mass*1.3:
                if (virus.x-self.x)**2+(virus.y-self.y)**2 < (self.radius-virus.radius/3)**2:
                    if self.id not in Globals.objects_to_delete and virus.id not in Globals.objects_to_delete:
                        self.consume_virus(virus)

       
    def eject_mass(self):
        e = Ejected(self)
        self.mass -= Globals.ejected_loss
        self.radius = math.sqrt(self.mass)
        Globals.ejected.append(e)


    def check_colliding(self, cells):

       
        for thing in self.player.cells:
           
            if thing.id != self.id:
                sq_distance = ((thing.x-self.x)**2+(thing.y-self.y)**2)
                if sq_distance < (thing.radius+self.radius)**2:
                    # If cells are too young, repel each other
                    if (time.time()-thing.time_created < Globals.player_recombine_time*(self.mass**(1/4)/4) or time.time()-self.time_created < Globals.player_recombine_time*(self.mass**(1/4)/4)) and thing.player == self.player:
                        if time.time()-thing.time_created > .2 and time.time()-self.time_created > .2:
                            for i in range(10):
                                if self.touching(thing):
                                    try:
                                        xdiff = self.x-thing.x
                                        ydiff = self.y-thing.y
                                        distance_squared = xdiff**2+ydiff**2
                                        xforce = xdiff/distance_squared*250
                                        yforce = ydiff/distance_squared*250
                                        self.x += xforce*Globals.gamespeed
                                        self.y += yforce*Globals.gamespeed
                                        thing.x -= xforce*Globals.gamespeed
                                        thing.y -= yforce*Globals.gamespeed
                                    except Exception as e: print(str(e) + " At cell collision")

                    # If cells are old enough, recombine
                    else:
                        if sq_distance < (self.radius-thing.radius/3)**2:
                            if self.id not in Globals.objects_to_delete and thing.id not in Globals.objects_to_delete:
                                self.consume(thing)

        for thing in cells:
            if thing.player != self.player:
                sq_distance = (thing.x-self.x)**2+(thing.y-self.y)**2
                if sq_distance < (thing.radius+self.radius)**2:
                    if self.id not in Globals.objects_to_delete and thing.id not in Globals.objects_to_delete:
                        if self.mass >= thing.mass*1.3 and sq_distance < (self.radius-thing.radius/3)**2:
                                self.consume(thing)
                        elif thing.mass >= self.mass*1.3 and sq_distance < (thing.radius-self.radius/3)**2:
                                thing.consume(self)