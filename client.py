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
from _thread import *
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
from common.serverinfo import ServerInfo
from common.clientinfo import ClientInfo
from common.colors import Colors
import cProfile
import re

"""
Todo:
optimize game
make it so when one cell increases mass, camera moves smoothly
idk
"""

def game_tick():
    player.update_target(Globals.camera, Globals.agars)
    info.target = player.target


def game_draw():
    target_camera_x, target_camera_y = player.calc_center_of_mass()
    Globals.camera.set_pos(target_camera_x, target_camera_y)
    Globals.camera.tick()
    all_objs = list(all_drawable())
    all_objs.sort(key=lambda x: x.radius)
    for obj in all_objs:
        obj.draw(window, Globals.camera)


def interpolate():

    Globals.tickrate = 1/delta_time
    Globals.gamespeed = delta_time

    all_objs = list(all_drawable(agars_ = False, ejected_ = True, viruses_ = False, brown_viruses_ = False, cells_ = True))
    for thing in all_objs:
        thing.tick()


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

#read values from a section
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



screen_width, screen_height = 1280, 720
screen_fullscreen : bool = False
window = pygame.display.set_mode([screen_width, screen_height], pygame.RESIZABLE)
clock = pygame.time.Clock()
pygame.display.set_caption("Agar.io Clone")

#virus_image = pygame.image.load("resources/images/virus.png")

aa_agar = True

background_color = Colors.black
font_color = Colors.green




Globals.camera = Camera(window)



frames = 0


ejected_to_calculate = set()



font = 'arial'
font_width = int(screen_width/100+1)
dialogue_font = pygame.font.SysFont(font, font_width)







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



playing = True
aa_text = True



info = ClientInfo()

def update(change):
    count = 0

    if change == None:
        return 0
    
    while change != None:
        one_update(change)
        Globals.players = change.players
        Globals.cells = change.cells
        Globals.ejected = change.ejected
        change = change.next_batch
        count += 1


    
    return count

def use_data(data):
    # players = data.players
    Globals.agars = data.agars
    Globals.viruses = data.viruses
    Globals.brown_viruses = data.brown_viruses
    Globals.ejected = data.ejected
    Globals.cells = data.cells
    Globals.players = data.players

def one_update(update):
    
    for obj in update.objects_added:
        if type(obj) == Agar:
            Globals.agars.add(obj)
        elif type(obj) == Virus:
            Globals.viruses.append(obj)
        elif type(obj) == BrownVirus:
            Globals.brown_viruses.append(obj)
    Globals.agars = set([agar for agar in Globals.agars if agar.id not in update.objects_deleted])
    Globals.viruses = [virus for virus in Globals.viruses if virus.id not in update.objects_deleted]
    Globals.brown_viruses = [agar for agar in Globals.brown_viruses if agar.id not in update.objects_deleted]

n = Network()
info_ = n.getId()
use_data(info_)
player_id = info_.player.id

delta_time = 1/Globals.tickrate

def threaded_update(useless, useless2):
    while True:
        changes = n.send(info)
        update(changes)

start_new_thread(threaded_update (1, 2))

while playing:
    start = time.time()
    #cProfile.run('game_tick()', sort='cumtime')

    Globals.cells.sort(key=lambda x: x.mass, reverse=False)
    
    window.fill(background_color)


    

    interpolate()

    info.split = False
    info.eject = False




    for p in Globals.players:
        if p.id == player_id:
            player = p

             

    target_scale = 0
    for thing in player.cells:
        target_scale += thing.radius**(1/4)/10
       

    target_scale/= max(len(player.cells)**(1/1.5), 1)

    Globals.camera.set_scale(max(target_scale, .1))

    total_mass = sum(cell.mass for cell in player.cells)
                

                   
               
   
    if Globals.camera.scale > 1:
        aa_agar = False
    else:
        aa_agar = True
   
    for event in pygame.event.get():
       
        if event.type == pygame.QUIT:
            playing = False
            break
        
        if event.type == pygame.VIDEORESIZE:
            screen_width, screen_height = window.get_size()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                playing = False
                break

            if event.key == pygame.K_SPACE:
                info.split = True

            if event.key == pygame.K_w:
                info.eject = True

            if event.key == pygame.K_F11:
                screen_fullscreen = not screen_fullscreen
                if screen_fullscreen:
                    pygame.display.set_mode((0,0), pygame.FULLSCREEN)
                else:
                    pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
                screen_width, screen_height = window.get_size()
    if pygame.key.get_pressed()[pygame.K_e]:
        info.eject = True
    if pygame.key.get_pressed()[pygame.K_z]:
        info.split = True
                

    game_tick()
    game_draw()


    dialogue = dialogue_font.render("Mass: " + str(int(total_mass+.5)), aa_text, font_color)
    window.blit(dialogue, (0, 0))
    dialogue = dialogue_font.render("FPS: " + str(Globals.fps_), aa_text, font_color)
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

    pygame.display.flip()


    delta_time = time.time()-start
    clock.tick(fps)
    if frames % int(fps/2) == 0:
        Globals.fps_ = round(1/(time.time()-start))
        last_time = time.time()
    frames += 1


pygame.quit()