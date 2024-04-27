import pygame
import pygame.gfxdraw
import math
import random
import time
from configparser import ConfigParser
import cProfile
import re
from network import Network
import pickle

import pygame
import pygame.gfxdraw
import math
import random
import time
from configparser import ConfigParser
from common.player import Player
from common.cell import Cell
from common.agar import Agar
from common.camera import Camera
from common.drawable import Drawable
from common.globals import Globals
from common.virus import Virus
from common.brownvirus import BrownVirus
from common.serverinfo import Info
import cProfile
import re

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
        window.blit(self.image, Globals.camera.get_screen_pos(self.x, self.y))



def mouse_in_game_pos():
    x,y = pygame.mouse.get_pos()
    return((x+Globals.camera.x)*Globals.camera.scale, (y+Globals.camera.y)*Globals.camera.scale)

def new_cell(player, color):
    new_cell = Cell(random.randint(-border_width, border_width), random.randint(-border_height, border_height), player_start_mass, color, player)
    Globals.cells.append(new_cell)
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

def game_draw():
    global draw_time
    timer_start = time.time()
    all_objs = list(all_drawable())
    all_objs.sort(key=lambda x: x.radius)
    for obj in all_objs:
        obj.draw(window, Globals.camera)
    draw_time += time.time()-timer_start

def game_tick():
    global draw_time
    global cell_time
    global agar_time
    global virus_time
    global ejected_time

    target_camera_x, target_camera_y = calc_center_of_mass(player.cells)
    target_camera_x = target_camera_x/Globals.camera.scale-width/2
    target_camera_y = target_camera_y/Globals.camera.scale-height/2
    #camera.x += (target_camera_x-camera.x)/1
    #camera.y += (target_camera_y-camera.y)/1
    Globals.camera.set_pos(target_camera_x, target_camera_y)
    Globals.camera.tick()

    timer_start = time.time()

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

    
    all_objs = list(all_drawable())
    for thing in all_objs:
        if type(thing) != Cell:
            thing.tick()

    timer_start = time.time()

    for player_ in Globals.players:
        player_.update_target(Globals.camera, Globals.agars)
        player_.tick()

    cell_time += time.time()-timer_start



def near_cells(thing):
    for cell in Globals.cells:
        if abs(cell.x-thing.x) < cell.radius+20:
            if abs(cell.y-thing.y) < cell.radius+20:
                if (cell.x-thing.x)**2+(cell.y-thing.y)**2 < (cell.radius+20)**2:
                    return True

    return False

def all_drawable(agars_ = True, ejected_ = True, viruses_ = True, brown_viruses_ = True, cells_ = True):
    if agars_:
        for agar in Globals.agars:
            yield agar
    if ejected_:
        for e in Globals.ejected:
            yield e
    if viruses_:
        for virus in Globals.viruses:
            yield virus
    if brown_viruses_:
        for brown_virus in Globals.brown_viruses:
            yield brown_virus
    if cells_:
        for cell in Globals.cells:
            yield cell

def all_consumable():
    for e in Globals.ejected:
        yield e
    for v in Globals.viruses:
        yield v
    for brown_virus in Globals.brown_viruses:
         yield brown_virus
    for cell in Globals.cells:
         yield cell




pygame.init()

config = ConfigParser()

# parse existing file
config.read('common/agar.ini')

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




Globals.camera = Camera()
Globals.camera.x = 0
Globals.camera.y = 0
target_scale = 105



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

player = Player("player", Colors.blue)
Globals.players.append(player)
for i in range(bot_count):
    Globals.players.append(Player("bot", Colors.red))
for i in range(minion_count):
    Globals.players.append(Player("minion", Colors.green))

player_names = ["Player", "Bot 1", "Bot 2", "Bot 3", "Bot 4", "Bot 5", "Bot 6", "Bot 7", "Bot 8", "Bot 9", "Bot 10"]

fps_ = fps

last_time = time.time()

for i in range(int(max_agars/2)):
    rand_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    Globals.agars.add(Agar(random.randint(-border_width, border_width), random.randint(-border_height, border_height), agar_min_mass, rand_color))

for i in range(int(virus_count)):
    Globals.viruses.append(Virus(random.randint(-border_width, border_width), random.randint(-border_height, border_height), virus_mass, Colors.green))

for i in range(int(brown_virus_count)):
    Globals.brown_viruses.append(BrownVirus(random.randint(-border_width, border_width), random.randint(-border_height, border_height), brown_virus_mass, Colors.brown))


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
    # players = data.players
    Globals.agars = data.agars
    Globals.viruses = data.viruses
    Globals.brown_viruses = data.brown_viruses
    Globals.ejected = data.ejected
    Globals.cells = data.ejected
    Globals.players = data.players

    # ...

n = Network()
player_id = pickle.loads(n.getId()).id
#info = pickle.loads(sv_data)
# players = data.players
#Globals.agars = sv_data.agars

while playing:
    start = time.time()
    #cProfile.run('game_tick()', sort='cumtime')

    Globals.cells.sort(key=lambda x: x.mass, reverse=False)
    
    window.fill(background_color)

    use_data(n.send(player))




    for p in Globals.players:
        if p.id == player_id:
            player = p
             


    if len(Globals.viruses) < virus_count:
        new_virus = Virus(random.randint(-border_width, border_width), random.randint(-border_height, border_height), virus_mass, Colors.green)
        while len([c for c in Globals.cells if new_virus.touching(c)]) != 0:
            new_virus = Virus(random.randint(-border_width, border_width), random.randint(-border_height, border_height), virus_mass, Colors.green)
        Globals.viruses.append(new_virus)

    if len(Globals.brown_viruses) < brown_virus_count:
        Globals.brown_viruses.append(BrownVirus(random.randint(-border_width, border_width), random.randint(-border_height, border_height), brown_virus_mass, Colors.brown))
   
    # if len(Globals.agars) < max_agars:
    #     if frames%int(len(Globals.agars)/25000*fps+1) == 0:
    #         rand_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    #         Globals.agars.add(Agar(random.randint(-border_width, border_width), random.randint(-border_height, border_height), agar_min_mass, rand_color))

    target_scale = 0
    for thing in player.cells:
        target_scale += thing.radius**(1/4)/10
       

    target_scale/= max(len(player.cells)**(1/1.5), 1)

    Globals.camera.set_scale(1)

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
                

                   
               
   
    if Globals.camera.scale > 1:
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

            if event.key == pygame.K_SPACE:
                player.split()

            if event.key == pygame.K_w:
                player.eject_mass()

            if event.key == pygame.K_f:
                for p in Globals.players:
                    if p.mode == "minion":
                        p.split()
            if event.key == pygame.K_g:
                for p in Globals.players:
                    if p.mode == "minion":
                        p.eject_mass()
            if event.key == pygame.K_F11:
                if width == 1920:
                        width, height = 1280, 720
                if width == 1280:
                        width, height = 1920, 1080
                window = pygame.display.set_mode([width, height])
    if pygame.key.get_pressed()[pygame.K_e]:
        for thing in player.cells:
            if thing.mass > player_eject_min_mass and thing.mass > ejected_loss:
                thing.eject_mass()
    if pygame.key.get_pressed()[pygame.K_z]:
        player.split()
                

    start_tick_time = time.time()
    game_tick()
    tick_time += time.time()-start_tick_time
    game_draw()


    dialogue = dialogue_font.render("Mass: " + str(int(total_mass+.5)), aa_text, font_color)
    window.blit(dialogue, (0, 0))
    dialogue = dialogue_font.render("FPS: " + str(fps_), aa_text, font_color)
    dialogue_rect = dialogue.get_rect(center=(100, 100))
    window.blit(dialogue, dialogue_rect)
   
    dialogue = dialogue_font.render("Cells: " + str(len(Globals.cells)), aa_text, font_color)
    dialogue_rect = dialogue.get_rect(center=(100, 125))
    window.blit(dialogue, dialogue_rect)
    dialogue = dialogue_font.render("PLAYERS: " + str(len(Globals.players)), aa_text, font_color)
    dialogue_rect = dialogue.get_rect(center=(100, 150))
    window.blit(dialogue, dialogue_rect)
    dialogue = dialogue_font.render("AGARS: " + str(len(Globals.agars)), aa_text, font_color)
    dialogue_rect = dialogue.get_rect(center=(100, 175))
    window.blit(dialogue, dialogue_rect)
    dialogue = dialogue_font.render("Ejected: " + str(len(Globals.ejected)), aa_text, font_color)
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


    Globals.agars = set([agar for agar in Globals.agars if agar.id not in Globals.objects_to_delete])
    Globals.ejected = [ejected_mass for ejected_mass in Globals.ejected if ejected_mass.id not in Globals.objects_to_delete]
    Globals.cells = [cell for cell in Globals.cells if cell.id not in Globals.objects_to_delete]
    Globals.viruses = [virus for virus in Globals.viruses if virus.id not in Globals.objects_to_delete]
    Globals.brown_viruses = [brown_virus for brown_virus in Globals.brown_viruses if brown_virus.id not in Globals.objects_to_delete]
    objects = [obj for obj in objects if obj.id not in Globals.objects_to_delete]
    for cell in Globals.cells:
        if cell.mass > player_max_cell_mass:
            cell.split()
    for i in range(len(Globals.players)):
        thing = player.cells
        if len(thing) < 1:
             Globals.cells.append(Cell(random.randint(-border_width, border_width), random.randint(-border_height, border_height), player_start_mass, Colors.red, Globals.players[i]))
    for p in Globals.players:
        p.cells = [cell for cell in p.cells if cell.id not in Globals.objects_to_delete]

    Globals.objects_to_delete = set()

   

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



