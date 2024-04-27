import pygame
import pygame.gfxdraw
import math
import random
import time
from configparser import ConfigParser
import cProfile
import re
from network import Network

"""
Todo:
optimize game
make it so when one cell increases mass, camera moves smoothly
idk
"""


class Colors:
    white = (255, 255, 255)
    black = (0, 0, 0)

    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    blue = (25, 55, 225)

    light_red = (255, 64, 64)
    dark_red = (128, 0, 0)
    light_green = (64, 255, 64)
    dark_green = (0, 128, 0)    

    yellow = (255, 255, 0)
    purple = (255, 0, 255)
    turquoise = (0, 255, 255)
    cyan = turquoise

    brown = (139,69,19)
    brown = (139,69,19)
    brown = (150,75,0)

    gray = (128, 128, 128)
    dark_gray = (64, 64, 64)
    light_gray = (192, 192, 192)
    light_blue = (102, 178, 255)
    dark_blue = (0, 0, 192)

class Sprite:
    def __init__(self, image, x, y, rotation):
        self.x = x
        self.y = y
        self.ogimage = image
        self.image = self.ogimage
        self.rotation = rotation

    def draw(self):
        self.image = pygame.transform.rotate(self.ogimage, self.rotation)
        window.blit(self.image, camera.get_screen_pos(self.x, self.y))

class Camera:
    def __init__(self):
        self.pos_smoothness = 0
        self.scale_smoothness = .2

        self.scale = .15
        self.target_scale = self.scale

        self.x = 0
        self.y = 0
        self.target_x = self.x
        self.target_y = self.y

   

        self.xspeed = 0
        self.yspeed = 0

        
        self.multiplicative_friction = .8
        self.flat_friction = .1

    def tick(self):
        #pass
        # if self.pos_smoothness*fps > 1:
        #     self.x += (self.target_x-self.x)/(self.pos_smoothness*fps)
        #     self.y += (self.target_y-self.y)/(self.pos_smoothness*fps)
        # else:
        #     self.x, self.y = self.target_x,self.target_y

        if (self.scale_smoothness*fps) > 1:
            self.scale += (self.target_scale-camera.scale)/(self.scale_smoothness*fps)
        else:
            self.scale = self.target_scale
    
    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def set_scale(self, scale):
        self.scale = scale
        self.target_scale = scale

    def get_screen_pos(self, x, y):
        return (x/self.scale-self.x), (y/self.scale-self.y)
    
    def on_screen(self, x, y, radius):
        pass

    def get_screen_x(self, x):
        return (x/self.scale-self.x)

    def get_screen_y(self, y):
        return (y/self.scale-self.x)
        
class Drawable:
    def __init__(self, x, y, mass, color):
        global drawable_count

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
        self.id = drawable_count
        drawable_count += 1
        self.consumer = False
        self.consumable = True


    def draw(self, aa=True, outline=True):
             
        self.radius = math.sqrt(self.mass)
        self.outline_thickness = round(math.sqrt(self.smoothradius/camera.scale)/2)
        self.smoothradius += (self.radius - self.smoothradius)/smoothness

        #Draw Outline
        if self.outline_thickness > 0 and outline:
            if aa:
                pygame.gfxdraw.aacircle(window, round(self.x/camera.scale-camera.x), round(self.y/camera.scale-camera.y), round(abs(self.smoothradius/camera.scale)), self.outline_color)
            pygame.gfxdraw.filled_circle(window, round(self.x/camera.scale-camera.x), round(self.y/camera.scale-camera.y), round(abs(self.smoothradius/camera.scale)), self.outline_color)
        
        #Draw Inside
        if aa:
            pygame.gfxdraw.aacircle(window, round(self.x/camera.scale-camera.x), round(self.y/camera.scale-camera.y), round(abs(self.smoothradius/camera.scale-self.outline_thickness)), self.color)
        pygame.gfxdraw.filled_circle(window, round(self.x/camera.scale-camera.x), round(self.y/camera.scale-camera.y), round(abs(self.smoothradius/camera.scale-self.outline_thickness)), self.color)


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
            if self.id not in objects_to_delete and other.id not in objects_to_delete:
                return self.mass > other.mass*1.3 and self.overlapping(other)
        return False

    def check_consume(self):
        global objects
        global objects_to_delete
        if self.consumer:
            for obj in all_drawable(agars_ = False):
                if self.can_consume(obj):
                    self.consume(obj)
         
    def consume(self, other):
        self.mass += other.mass
        objects_to_delete.add(other.id)
        
class Player:
    def __init__(self, mode, color):
        self.mode = mode
        self.color = color
        
        self.target = (0, 0)
        #self.cells = [new_cell(self, self.color)]
        self.cells = []
    
    def tick(self):

        self.target = self.get_target()
        for cell in self.cells:
            cell.target = self.target
            cell.tick()

    def split(self):
        for i in range(len(self.cells)):
            if len(self.cells) < player_max_cells:
                cell = self.cells[i]
                cell.split()
    def eject_mass(self):
        for cell in self.cells:
            if cell.mass > player_eject_min_mass:
                cell.eject_mass()

                

    def get_target(self):
        if self.mode == "player" or self.mode == "minion":
            x, y = pygame.mouse.get_pos()
            target = (x+camera.x)*camera.scale, (y+camera.y)*camera.scale
            
        
        elif self.mode == "bot":
            nearest_agar = self.get_nearest_agar()
            target = nearest_agar.x, nearest_agar.y


        else:
            target = (0, 0)

        return target
    
    def get_nearest_agar(self):
        center = calc_center_of_mass(self.cells)
        mindist = 2147483646
        minagar = Agar(0, 0, 1, Colors.green)
        for agar in agars:
            dist_sq = (center[0]-agar.x)**2+(center[1]-agar.y)**2
            if dist_sq < mindist:
                mindist = dist_sq
                minagar = agar
        return minagar

class Cell(Drawable):
   
    def __init__(self, x, y, mass, color, player):
        super().__init__(x, y, mass, color)
        self.consumer = True
        self.consumable = True
        self.extraxspeed = 0
        self.extrayspeed = 0
        self.slow_zone = 10
        self.speed = player_speed
        self.xspeed = 0
        self.yspeed = 0
        self.inertia = 5
        self.smoothradius = self.radius
        self.player = player
        self.target = player.target


        self.time_created = time.time()

    def draw(self):
        super().draw()

        player_font_width = int(self.radius/camera.scale/2+1)
        dialogue_font = pygame.font.SysFont(font, player_font_width)
        
        # Draw Player Name
        dialogue = dialogue_font.render(self.player.mode, aa_text, Colors.white)
        dialogue_rect = dialogue.get_rect(center = (round(self.x/camera.scale-camera.x), round(self.y/camera.scale-camera.y)))
        window.blit(dialogue, dialogue_rect)

        # Draw cell mass
        dialogue = dialogue_font.render(str(int(self.mass)), aa_text, Colors.white)
        dialogue_rect = dialogue.get_rect(center = (round(self.x/camera.scale-camera.x), round(self.y/camera.scale-camera.y+player_font_width)))
        window.blit(dialogue, dialogue_rect)


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




        if fps_ < fps/smooth_fix_limit or fps_ > fps*smooth_fix_limit:
            self.xspeed = velocity*vector[0]*self.speed/fps*smooth_fix_limit
            self.yspeed = velocity*vector[1]*self.speed/fps*smooth_fix_limit

        else:
            self.xspeed = velocity*vector[0]*self.speed/fps_
            self.yspeed = velocity*vector[1]*self.speed/fps_


        self.x += (self.xspeed+self.extraxspeed)/math.sqrt(self.radius)
        self.y += (self.yspeed+self.extrayspeed)/math.sqrt(self.radius)

        if self.x > border_width:
            self.x = border_width
        if self.x < -border_width:
            self.x = -border_width

        if self.y > border_height:
            self.y = border_height
        if self.y < -border_height:
            self.y = -border_height

        self.extraxspeed /= 1.05
        self.extrayspeed /= 1.05

    def split(self):
        
        if len(self.player.cells) > player_max_cells or self.mass < player_split_min_mass:
                return
        
        self.mass /= 2
        new_cell = Cell(self.x, self.y+.1, self.mass, self.color, self.player)
        cells.append(new_cell)
        self.player.cells.append(new_cell)
        

        extrax = (self.xspeed)/fps*100
        extray = (self.yspeed)/fps*100



       
       
        total_speed = math.sqrt(extrax**2+extray**2)
       
        if extrax**2+extray**2 > player_speed**2*2:
                percent_x = extrax/total_speed
                percent_y = extray/total_speed

               
                       
               
                extrax = player_speed*percent_x*2
                extray = player_speed*percent_y*2

        cells[len(cells)-1].extraxspeed = extrax*cells[len(cells)-1].radius**(2/3)
        cells[len(cells)-1].extrayspeed = extray*cells[len(cells)-1].radius**(2/3)


    def tick(self):
        self.apply_physics()
       
    def apply_physics(self):
        if self.mass > player_min_mass:
            if fps_ < fps/smooth_fix_limit or fps_ > fps*smooth_fix_limit:
                self.mass -= self.mass*player_decay_rate/fps
            else:
                self.mass -= self.mass*player_decay_rate/fps_
               
        self.move()
        self.check_colliding(cells)
        self.check_viruses(brown_viruses)



    def consume_virus(self, virus):
        self.mass += virus.mass
        objects_to_delete.add(virus.id)
        while len(self.player.cells) < player_max_cells and self.mass > player_split_min_mass:
                self.split()


    def consume_brown_virus(self, virus):
        self.mass += virus.mass
        objects_to_delete.add(virus.id)
        while len(self.player.cells) < player_max_cells and self.mass > player_split_min_mass:
                self.split()  
               
   

    def check_viruses(self, viruses):
        for virus in viruses:
            if self.mass*1.3 < virus.mass:
                if (virus.x-self.x)**2+(virus.y-self.y)**2 < (virus.radius-self.radius/3)**2:
                    if self.id not in objects_to_delete and virus.id not in objects_to_delete:
                        virus.consume(self)
            if self.mass > virus.mass*1.3:
                if (virus.x-self.x)**2+(virus.y-self.y)**2 < (self.radius-virus.radius/3)**2:
                    if self.id not in objects_to_delete and virus.id not in objects_to_delete:
                        self.consume_virus(virus)

       
    def eject_mass(self):
        e = Ejected(self)
        self.mass -= ejected_loss
        self.radius = math.sqrt(self.mass)
        ejected.append(e)

    def check_colliding(self, cells):
        global player_recombine_time

       
        for thing in self.player.cells:
           
            if thing.id != self.id:
                sq_distance = ((thing.x-self.x)**2+(thing.y-self.y)**2)
                if sq_distance < (thing.radius+self.radius)**2:
                    # If cells are too young, repel each other
                    if (time.time()-thing.time_created < player_recombine_time*(self.mass**(1/4)/4) or time.time()-self.time_created < player_recombine_time*(self.mass**(1/4)/4)) and thing.player == self.player:
                        if time.time()-thing.time_created > .2 and time.time()-self.time_created > .2:
                            for i in range(10):
                                if self.touching(thing):
                                    try:
                                        xdiff = self.x-thing.x
                                        ydiff = self.y-thing.y
                                        distance_squared = xdiff**2+ydiff**2
                                        xforce = xdiff/distance_squared*250
                                        yforce = ydiff/distance_squared*250
                                        self.x += xforce/fps
                                        self.y += yforce/fps
                                        thing.x -= xforce/fps
                                        thing.y -= yforce/fps
                                    except Exception as e: print(str(e) + " At cell collision")

                    # If cells are old enough, recombine
                    else:
                        if sq_distance < (self.radius-thing.radius/3)**2:
                            if self.id not in objects_to_delete and thing.id not in objects_to_delete:
                                self.consume(thing)

        for thing in cells:
            if thing.player != self.player:
                sq_distance = (thing.x-self.x)**2+(thing.y-self.y)**2
                if sq_distance < (thing.radius+self.radius)**2:
                    if self.id not in objects_to_delete and thing.id not in objects_to_delete:
                        if self.mass >= thing.mass*1.3 and sq_distance < (self.radius-thing.radius/3)**2:
                                self.consume(thing)
                        elif thing.mass >= self.mass*1.3 and sq_distance < (thing.radius-self.radius/3)**2:
                                thing.consume(self)

class Agar(Drawable):

    def __init__(self, x, y, mass, color):
        super().__init__(x, y, mass, color)

    def draw(self):
        super().draw(False, False)


    def tick(self):
        global cells
        self.check_colliding(cells)
        self.x += self.xspeed
        self.y += self.yspeed
        self.xspeed /= 1+(12/fps)
        self.yspeed /= 1+(12/fps)
        if abs(self.xspeed) < .01:
            self.xspeed = 0
        if abs(self.yspeed) < .01:
            self.yspeed = 0

        if self.x > border_width:
            self.x = border_width
            self.xspeed *= -.5
        if self.x < -border_width:
            self.x = -border_width
            self.xspeed *= -.5
        if self.y > border_height:
            self.y = border_height
            self.yspeed *= -.5
        if self.y < -border_height:
            self.y = -border_height
            self.yspeed *= -.5
        
        if agar_grow:
            if self.mass < agar_max_mass and random.randint(0, round(fps/agar_grow_speed)) == 1:
                self.grow()

    def grow(self):
        self.mass += 1


    def check_colliding(self, cells):
        for thing in cells:
            if thing.can_consume(self):
                thing.consume(self)

class Ejected(Drawable):

    def __init__(self, cell):
        
        global ejected_size
        global ejected_loss
        global eject_min_size
        global ejected_speed
        super().__init__(cell.x, cell.y, ejected_size, cell.color)
       
        x, y = cell.target
        xdiff = x-cell.x
        ydiff = y-cell.y
        angle = math.atan2(ydiff, xdiff)+random.uniform(-.1, .1)
        vector = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        self.x = self.x+(cell.radius)*vector[0]
        self.y = self.y+(cell.radius)*vector[1]
        self.xspeed = vector[0]*ejected_speed*60
        self.yspeed = vector[1]*ejected_speed*60
        self.time_created = time.time()

    def tick(self):
        global ejected_to_calculate
        self.radius = math.sqrt(self.mass)
        self.smoothradius += (self.radius - self.smoothradius)/smoothness
        global ejected_size
        self.x += self.xspeed/fps
        self.y += self.yspeed/fps

        self.xspeed /= 1+(6/fps)
        self.yspeed /= 1+(6/fps)


        if self.x > border_width:
            self.x = border_width
            self.xspeed *= -.5
        if self.x < -border_width:
            self.x = -border_width
            self.xspeed *= -.5
        if self.y > border_height:
            self.y = border_height
            self.yspeed *= -.5
        if self.y < -border_height:
            self.y = -border_height
            self.yspeed *= -.5
           
       
        



        self.check_colliding(cells)
        self.check_brown(brown_viruses)

        # Repel other Ejected
        for other in ejected:
            if other.id != self.id:
                if self.touching(other):
                    try:
                        xdiff = self.x-other.x
                        ydiff = self.y-other.y
                        distance_squared = xdiff**2+ydiff**2
                        xforce = xdiff/distance_squared*50
                        yforce = ydiff/distance_squared*50
                        self.x += xforce/fps
                        self.y += yforce/fps
                        other.x -= xforce/fps
                        other.y -= yforce/fps
                    except Exception as e: print(e + " At ejected collision")
        
        # Consume other ejected

        # for mass in ejected:
        #         if mass.x != self.x and mass.y != self.y:
        #                 if ((self.x-mass.x)**2+(self.y-mass.y)**2) < (self.radius/2+mass.radius/2)**2 and mass.id not in objects_to_delete and self.id not in objects_to_delete and self.mass >= mass.mass:
        #                         self.consume(mass)


    def check_colliding(self, cells):
        #if time.time() - self.time_created >= 0.3:
        for thing in cells:
            if thing.can_consume(self):
                thing.consume(self)


    def check_brown(self, brown_viruses):
        for virus in brown_viruses:
            if self.id not in objects_to_delete:
                if (self.x-virus.x)**2+(self.y-virus.y)**2 < (virus.radius)**2:
                    virus.consume(self)

class Virus(Drawable):

    def __init__(self, x, y, mass, color):
        super().__init__(x, y, mass, color)

    def tick(self):
        self.check_colliding(cells)

    def check_colliding(self, cells):
        for thing in cells:
            if self.id not in objects_to_delete:
                if thing.mass >= virus_mass*1.3 and abs(self.x-thing.x)**2+abs(self.y-thing.y)**2 < (self.radius/4+thing.radius)**2:
                    thing.consume_virus(self)

class BrownVirus(Drawable):
    def __init__(self, x, y, mass, color):
        super().__init__(x, y, mass, color)
        self.consumer = True
        self.spit_rate = 120
        self.startmass = mass
        self.smoothradius = self.radius

    def tick(self):
        spit_rate = 120
        if fps < spit_rate:
            for i in range(round(spit_rate/fps)):
                if self.mass > self.startmass:
                    self.spit()
        else:
            if (frames%(round(fps/spit_rate)) == 0):
                if self.mass > self.startmass:
                    self.spit()
        
        if random.randint(0, fps) == 0 and len(agars) < max_agars:
            self.spit() 

        self.check_consume()
            

    def spit(self):
        spit_mult = 1
        spit_mass = 1
        spit_speed = random.uniform(.8, 1)
        rand_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        angle = random.uniform(0, 360)
        vector = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        spatted_x = self.x+(self.radius-math.sqrt(spit_mass))*vector[0]
        spatted_y = self.y+(self.radius-math.sqrt(spit_mass))*vector[1]
        spatted = Agar(spatted_x, spatted_y, spit_mass, rand_color)
        spatted.xspeed = vector[0]*spit_speed
        spatted.yspeed = vector[1]*spit_speed
        agars.add(spatted)
        self.mass -= spatted.mass/spit_mult
        self.mass = max(self.mass, self.startmass)
       

       

    def colliding(self, thing):
        return abs(self.x-thing.x)**2+abs(self.y-thing.y)**2 < (self.radius/4+thing.radius)**2


    # def consume_ejected(self, thing):
    #     self.mass += thing.mass
    #     objects_to_delete.add(thing.id)

    # def consume_cell(self, cell):
    #     self.mass += cell.mass
    #     objects_to_delete.add(cell.id)
       

def mouse_in_game_pos():
    x,y = pygame.mouse.get_pos()
    return((x+camera.x)*camera.scale, (y+camera.y)*camera.scale)

def new_cell(player, color):
    new_cell = Cell(random.randint(-border_width, border_width), random.randint(-border_height, border_height), player_start_mass, color, player)
    cells.append(new_cell)
    return new_cell

def calc_center_of_mass(bodies):
        try:
            center_x = 0
            center_y = 0
            weight = 0
            for body_ in bodies:
                center_x += body_.x*body_.mass
                center_y += body_.y*body_.mass
                weight += body_.mass
            return (center_x/weight, center_y/weight)
        except:
            print("divide by 0")
            return (10, 10)

def game_tick():
    global draw_time
    global cell_time
    global agar_time
    global virus_time
    global ejected_time

    target_camera_x, target_camera_y = calc_center_of_mass(player.cells)
    target_camera_x = target_camera_x/camera.scale-width/2
    target_camera_y = target_camera_y/camera.scale-height/2
    #camera.x += (target_camera_x-camera.x)/1
    #camera.y += (target_camera_y-camera.y)/1
    camera.set_pos(target_camera_x, target_camera_y)
    camera.tick()

    timer_start = time.time()


       
    # cell_time += time.time()-timer_start


    #Bot AI (I think idk I wrote this like 2 yrs ago)
    # for bot in players:
    #     if bot != players[player]: #Make sure not to control player, only bots
    #         for cell in bot:
    #             target_cell = cell.target
    #             #Bots will split for their target if they can, (only if they are in two or less pieces - should add this, also why is this done for each cell wtf)
                
    #             if target_cell.mass*2.6 < cell.mass and target_cell.id not in objects_to_delete:
    #                     if (cell.x-target_cell.x)**2+(cell.y-target_cell.y)**2 < cell.radius**2*2:
    #                         for bruh in bot:
    #                                 bruh.split()
    #                         break

    # timer_start = time.time()

    # #AGARS
   
    # for thing in agars_to_draw:
    #     thing.check_colliding(cells)

    # # for thing in agars:
    # #     if aa_agar:
    # #         thing.draw_high_quality()
    # #     if thing.id not in agar_to_delete:
    # #         thing.draw()

       
       
    # agar_time += time.time()-timer_start


    # timer_start = time.time()
    # for thing in ejected:
    #     thing.tick()
    # ejected_time += time.time()-timer_start

    # timer_start = time.time()
    # for thing in viruses:
    #     thing.tick()
   


    # for thing in brown_viruses:
    #     thing.tick()
    
    all_objs = list(all_drawable())
    all_objs.sort(key=lambda x: x.radius)
    for thing in all_objs:
        if type(thing) != Cell:
            thing.tick()

    timer_start = time.time()

    for player_ in players:
        player_.tick()

    cell_time += time.time()-timer_start

    timer_start = time.time()

    for obj in all_objs:
        obj.draw()
    draw_time += time.time()-timer_start

def near_cells(thing):
    for cell in cells:
        if abs(cell.x-thing.x) < cell.radius+20:
            if abs(cell.y-thing.y) < cell.radius+20:
                if (cell.x-thing.x)**2+(cell.y-thing.y)**2 < (cell.radius+20)**2:
                    return True

    return False

def all_drawable(agars_ = True, ejected_ = True, viruses_ = True, brown_viruses_ = True, cells_ = True):
    if agars_:
        for agar in agars:
            yield agar
    if ejected_:
        for e in ejected:
            yield e
    if viruses_:
        for virus in viruses:
            yield virus
    if brown_viruses_:
        for brown_virus in brown_viruses:
            yield brown_virus
    if cells_:
        for cell in cells:
            yield cell

def all_consumable():
    for e in ejected:
        yield e
    for v in viruses:
        yield v
    for brown_virus in brown_viruses:
         yield brown_virus
    for cell in cells:
         yield cell




pygame.init()

config = ConfigParser()

# parse existing file
config.read('agar.ini')

# read values from a section
fps = config.getint('settings', 'fps')
speed = config.getfloat('settings', 'speed')

gamemode = config.getint('settings', 'gamemode')
border_width = config.getint('settings', 'border_width')
border_height = config.getint('settings', 'border_height')


max_agars = config.getint('settings', 'max_agars')
agar_min_mass = config.getint('settings', 'agar_min_mass')
agar_max_mass = config.getint('settings', 'agar_max_mass')
agar_grow = config.getboolean('settings', 'agar_grow')
agar_grow_speed = config.getfloat('settings', 'agar_grow_speed')



virus_count = config.getint('settings', 'virus_count')
virus_mass = config.getint('settings', 'virus_mass')

brown_virus_count = config.getint('settings', 'brown_virus_count')
brown_virus_mass = config.getint('settings', 'brown_virus_mass')


player_start_mass = config.getint('settings', 'player_start_mass')
player_speed = config.getfloat('settings', 'player_speed')
player_min_mass = config.getint('settings', 'player_min_mass')
player_max_cells = config.getint('settings', 'player_max_cells')
player_max_cell_mass = config.getint('settings', 'player_max_cell_mass')
player_decay_rate = config.getfloat('settings', 'player_decay_rate')
player_recombine_time = config.getfloat('settings', 'player_recombine_time')
player_eject_min_mass = config.getint('settings', 'player_eject_min_mass')
player_split_min_mass = config.getint('settings', 'player_split_min_mass')

agar_min_mass = 1
agar_max_mass = 4
max_agars = 3000

ejected_size = config.getint('settings', 'ejected_size')
ejected_loss = config.getint('settings', 'ejected_loss')
ejected_speed = config.getint('settings', 'ejected_speed')

bot_count = config.getint('settings', 'bot_count')
bot_start_mass = config.getint('settings', 'bot_start_mass')

minion_count = config.getint('settings', 'minion_count')
minion_start_mass = config.getint('settings', 'minion_start_mass')



width, height = 1280, 720

#virus_image = pygame.image.load("resources/images/virus.png")

aa_agar = True

background_color = Colors.black
font_color = Colors.green

objects_to_delete = set()


camera = Camera()
camera.x = 0
camera.y = 0
target_scale = 105


drawable_count = 0
frames = 0


ejected_to_calculate = set()



font = 'arial'
font_width = int(width/100+1)
dialogue_font = pygame.font.SysFont(font, font_width)
objects = []

pygame.display.set_caption("Agar.io Clone")

smoothness = 15


smooth_fix_limit = 4

window = pygame.display.set_mode([width, height])
clock = pygame.time.Clock()

agars = set()
cells = []
ejected = []
viruses = []
brown_viruses = []
players = []
player = Player("player", Colors.blue)
players.append(player)
for i in range(bot_count):
    players.append(Player("bot", Colors.red))
for i in range(minion_count):
    players.append(Player("minion", Colors.green))

player_names = ["Player", "Bot 1", "Bot 2", "Bot 3", "Bot 4", "Bot 5", "Bot 6", "Bot 7", "Bot 8", "Bot 9", "Bot 10"]

fps_ = fps

last_time = time.time()

for i in range(int(max_agars/2)):
    rand_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    agars.add(Agar(random.randint(-border_width, border_width), random.randint(-border_height, border_height), agar_min_mass, rand_color))

for i in range(int(virus_count)):
    viruses.append(Virus(random.randint(-border_width, border_width), random.randint(-border_height, border_height), virus_mass, Colors.green))

for i in range(int(brown_virus_count)):
    brown_viruses.append(BrownVirus(random.randint(-border_width, border_width), random.randint(-border_height, border_height), brown_virus_mass, Colors.brown))


draw_time = 0
cell_time = 0
agar_time = 0
virus_time = 0
ejected_time = 0
computational_time = 0
total_time = time.time()
tick_time = 0
playing = True
aa_text = True


def use_data(data):
    pass
    # players = data.players
    # agars = data.agars
    # ...

n = Network()
sv_data = n.getData() 
use_data(sv_data)

while playing:

    start = time.time()    
    window.fill(background_color)

    #sv_data = n.getData() 
    #use_data(sv_data)


   
    target_scale = 0
    for thing in player.cells:
        target_scale += thing.radius**(1/4)/10
       

    target_scale/= max(len(player.cells)**(1/1.5), 1)

    camera.set_scale(target_scale)

    total_mass = sum(cell.mass for cell in player.cells)

    #Bot AI Target finding
    # for thing in players:
    #     if thing != player:
    #         biggest = thing.cells[len(thing.cells)-1]

    #         # for thing2 in cells:
    #         #     if thing2.mass*1.3<biggest.mass and thing2.player != biggest.player:
    #         #         for buggin in thing:
    #         #             buggin.target = thing2
    #         target = get_nearest_agar(biggest)
    #         for cell in thing.cells:
    #             cell.target = target
                

                   
               
   
    if camera.scale > 1:
        aa_agar = False
    else:
        aa_agar = True
   
    for event in pygame.event.get():
       
        if event.type == pygame.QUIT:
            playing = False
            break

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                playing = False
                break

            # if event.key == pygame.K_SPACE:
            #     player.split()

            # if event.key == pygame.K_w:
            #     player.eject_mass()

            # if event.key == pygame.K_f:
            #     for p in players:
            #         if p.mode == "minion":
            #             p.split()
            # if event.key == pygame.K_g:
            #     for p in players:
            #         if p.mode == "minion":
            #             p.eject_mass()
            # if event.key == pygame.K_F11:
            #     if width == 1920:
            #             width, height = 1280, 720
            #     if width == 1280:
            #             width, height = 1920, 1080
            #     window = pygame.display.set_mode([width, height])
    # if pygame.key.get_pressed()[pygame.K_e]:
    #     for thing in player.cells:
    #         if thing.mass > player_eject_min_mass and thing.mass > ejected_loss:
    #             thing.eject_mass()
    # if pygame.key.get_pressed()[pygame.K_z]:
    #     player.split()
                

    start_tick_time = time.time()
    #game_tick()
    tick_time += time.time()-start_tick_time


    dialogue = dialogue_font.render("Mass: " + str(int(total_mass+.5)), aa_text, font_color)
    window.blit(dialogue, (0, 0))
    dialogue = dialogue_font.render("FPS: " + str(fps_), aa_text, font_color)
    dialogue_rect = dialogue.get_rect(center=(100, 100))
    window.blit(dialogue, dialogue_rect)
   
    dialogue = dialogue_font.render("Cells: " + str(len(cells)), aa_text, font_color)
    dialogue_rect = dialogue.get_rect(center=(100, 125))
    window.blit(dialogue, dialogue_rect)
    dialogue = dialogue_font.render("PLAYERS: " + str(len(players)), aa_text, font_color)
    dialogue_rect = dialogue.get_rect(center=(100, 150))
    window.blit(dialogue, dialogue_rect)
    dialogue = dialogue_font.render("AGARS: " + str(len(agars)), aa_text, font_color)
    dialogue_rect = dialogue.get_rect(center=(100, 175))
    window.blit(dialogue, dialogue_rect)
    dialogue = dialogue_font.render("Ejected: " + str(len(ejected)), aa_text, font_color)
    dialogue_rect = dialogue.get_rect(center=(100, 200))
    window.blit(dialogue, dialogue_rect)

    start_time = time.time()
    pygame.display.flip()
    flipping_time = time.time()-start_time
    computational_time += time.time()-start

   
    clock.tick(fps)
    if frames % int(fps/2) == 0:
        fps_ = round(1/(time.time()-start))
        last_time = time.time()
    frames += 1


    # agars = set([agar for agar in agars if agar.id not in objects_to_delete])
    # ejected = [ejected_mass for ejected_mass in ejected if ejected_mass.id not in objects_to_delete]
    # cells = [cell for cell in cells if cell.id not in objects_to_delete]
    # viruses = [virus for virus in viruses if virus.id not in objects_to_delete]
    # brown_viruses = [brown_virus for brown_virus in brown_viruses if brown_virus.id not in objects_to_delete]
    # objects = [obj for obj in objects if obj.id not in objects_to_delete]
    # for cell in cells:
    #     if cell.mass > player_max_cell_mass:
    #         cell.split()
    # for i in range(len(players)):
    #     thing = player.cells
    #     if len(thing) < 1:
    #          cells.append(Cell(random.randint(-border_width, border_width), random.randint(-border_height, border_height), player_start_mass, Colors.red, players[i]))
    # for p in players:
    #     p.cells = [cell for cell in p.cells if cell.id not in objects_to_delete]

    # objects_to_delete = set()

   

pygame.quit()

print("Draw time: " + str(draw_time))
print("Cell time: " + str(cell_time))
print("Ejected time: " + str(ejected_time))
print("Virus time: " + str(virus_time))
print("Agar time: " + str(agar_time))
print("Total time: " + str(time.time()-total_time))
print("Computational time: " + str(computational_time))
print("Flipping time: " + str(flipping_time))

print("Tick time: " + str(tick_time))

