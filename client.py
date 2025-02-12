import pygame
import pygame.gfxdraw
import math
import random
import time
import copy
from configparser import ConfigParser
import cProfile
import re
from network import Network
import pickle
from _thread import *
import threading
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
from common.actor import Actor
from common.globals import Globals
from common.virus import Virus
from common.brownvirus import BrownVirus
from common.serverinfo import ServerInfo
from common.serverchanges import ServerChanges
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
    info.minion_target = player.target

def game_draw():
    target_camera_x, target_camera_y = player.calc_center_of_mass()
    Globals.camera.set_pos(target_camera_x, target_camera_y)
    Globals.camera.tick()
    all_objs = [obj for obj in all_drawable() if Globals.camera.on_screen(obj)]
    all_objs.sort(key=lambda x: x.smoothradius)
    for obj in all_objs:
        obj.draw(window, Globals.camera)

def interpolate(dt):

    Globals.tickrate = 1/dt
    Globals.gamespeed = dt

    all_objs = list(all_drawable(agars_ = True, ejected_ = True, viruses_ = True, brown_viruses_ = True, cells_ = True))
    for thing in all_objs:
        thing.tick_client()
    
    # for thing in Globals.players:
    #     thing.tick_client()    

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

def display_metrics(window, spacing: int, aa_text: bool = True):
    font_color = Colors.green
    dialogue = Globals.dialogue_font.render(f"Fps: {Globals.fps_}", aa_text, font_color)
    window.blit(dialogue, (0, 0))
    dialogue = Globals.dialogue_font.render(f"Mass: {round(player.mass())}", aa_text, font_color)
    window.blit(dialogue, (0, spacing*3))
    dialogue = Globals.dialogue_font.render(f"Players:  {len(Globals.players)}", aa_text, font_color)
    window.blit(dialogue, (0, spacing*4))
    dialogue = Globals.dialogue_font.render(f"Cells: {len(Globals.cells)}", aa_text, font_color)
    window.blit(dialogue, (0, spacing*5))
    dialogue = Globals.dialogue_font.render(f"Agars: {len(Globals.agars)}", aa_text, font_color)
    window.blit(dialogue, (0, spacing*6))
    dialogue = Globals.dialogue_font.render(f"Ejected: {len(Globals.ejected)}", aa_text, font_color)
    window.blit(dialogue, (0, spacing*7))
    display_leaderboard(window, 10, spacing)

def display_leaderboard(window, size: int, spacing: int, aa_text: bool = True) -> None:
    screen_width, screen_height = window.get_size()
    font_color = Colors.green
    leaderboard = get_leaderboard(size)
    dialogue = Globals.dialogue_font.render('Leaderboard', aa_text, font_color)
    window.blit(dialogue, (screen_width-screen_width/10, screen_height/20)) 
    for i in range(len(leaderboard)):
        name = leaderboard[i]
        dialogue = Globals.dialogue_font.render(f'{i+1}. {name}', aa_text, font_color)
        window.blit(dialogue, (screen_width-screen_width/10, spacing*(i+1)+screen_height/20)) 

def get_leaderboard(size: int) -> list:
    leaderboard = []
    Globals.players.sort(key=lambda x: x.mass(), reverse=True)
    for player in Globals.players:
        if len(leaderboard) < size:
            leaderboard.append(player.name)
    return leaderboard

def update(change: ServerChanges):
    count = 0

    if change == None:
        return
    
    # Need loop in case more than one change
    while change != None:
        one_update(change)
        Globals.players = change.players
        Globals.ejected = change.ejected
        Globals.viruses = change.viruses
        #Globals.cells = change.cells
        for cell in Globals.cells:
            for c in change.cells:
                if cell.id == c.id:
                    cell.mass = c.mass
                    cell.extraxspeed = c.extraxspeed
                    cell.extrayspeed = c.extraxspeed
                    cell.x = c.x
                    cell.y = c.y
                    cell.xspeed = c.xspeed
                    cell.yspeed = c.yspeed
                    cell.player = c.player
                    cell.target = c.player.target
        for c in change.cells:
            if c.id not in [cell.id for cell in Globals.cells]:
                Globals.cells.append(c)
        for cell in Globals.cells:
            if cell.id not in [c.id for c in change.cells]:
                Globals.cells.remove(cell)

        for virus in Globals.brown_viruses:
            for v in change.brown_viruses:
                if virus.id == v.id:
                    virus.mass = v.mass
        for v in change.brown_viruses:
            if v.id not in [virus.id for virus in Globals.brown_viruses]:
                Globals.brown_viruses.append(v)
        for virus in Globals.brown_viruses:
            if virus.id not in [v.id for v in change.brown_viruses]:
                Globals.brown_viruses.remove(virus)
        #Globals.brown_viruses = change.brown_viruses
        count += 1
        #print(f"Change {count}")
        change = change.next_batch


    return count

def use_data(data):
    # players = data.players
    Globals.agars = data.agars
    Globals.viruses = data.viruses
    Globals.brown_viruses = data.brown_viruses
    Globals.ejected = data.ejected
    Globals.cells = data.cells
    Globals.players = data.players

def one_update(update: ServerChanges):

    for obj in update.objects_added:
        if type(obj) == Agar:
            Globals.agars.add(obj)
        # elif type(obj) == Virus:
        #     Globals.viruses.append(obj)
        # elif type(obj) == BrownVirus:
        #     Globals.brown_viruses.append(obj)
    Globals.agars = set([agar for agar in Globals.agars if agar.id not in update.objects_deleted])
    # Globals.viruses = [virus for virus in Globals.viruses if virus.id not in update.objects_deleted]
    # Globals.brown_viruses = [agar for agar in Globals.brown_viruses if agar.id not in update.objects_deleted

def threaded_update():
    global new_info, last_update
    while True:
        try:
            if new_info:
                changes: ServerChanges = n.send(info)
                with lock:
                    update(changes)
                    new_info = False
                    info.split = False
                    info.eject = False
                    info.minion_split = False
                    info.minion_eject = False
                    last_update = time.time()
        except Exception as e: 
            print(f'Exception {e} in threaded_update')
            return
        
last_update = time.time()
def main():
    global new_info, player, screen_width, last_update, screen_fullscreen
    frames = 0
    playing = True
    aa_text = True
    while playing:
        start = time.time()
        window.fill(background_color) 
        #cProfile.run('game_tick()', sort='cumtime')

        Globals.cells.sort(key=lambda x: x.mass, reverse=False)   
        dt = time.time()-last_update
        if dt > .001:
            with lock:
                interpolate(dt)
                last_update = time.time()
        new_info = True

        for p in Globals.players:
            if p.id == player_id:
                player = p 

        target_scale = 0
        for thing in player.cells:
            thing.update_radius()
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
                Globals.font_width = int(screen_width/100+1)
                Globals.dialogue_font = pygame.font.SysFont(Globals.font, Globals.font_width)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    playing = False
                    break

                if event.key == pygame.K_SPACE:
                    info.split = True

                if event.key == pygame.K_w:
                    info.eject = True

                if event.key == pygame.K_s:
                    info.minion_eject = True
                
                if event.key == pygame.K_d:
                    info.minion_split = True

                

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
                    
        with lock:
            game_tick()
            game_draw()


        display_metrics(window, screen_width/80)

        pygame.display.flip()


        delta_time = time.time()-start
        clock.tick(fps)
        #Why is delta_time before clock tick? wtf
        if frames % int(fps/2) == 0:
            Globals.fps_ = round(1/(time.time()-start))
            last_time = time.time()
        frames += 1


lock = threading.Lock()

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
screen_fullscreen: bool = False
window = pygame.display.set_mode([screen_width, screen_height], pygame.RESIZABLE)
clock = pygame.time.Clock()
pygame.display.set_caption("Agar.io Clone")

Globals.camera = Camera(window)

#virus_image = pygame.image.load("resources/images/virus.png")

aa_agar = True

background_color = Colors.black
font_color = Colors.green




ejected_to_calculate = set()

font = 'arial'
font_width = int(screen_width/100+1)
dialogue_font = pygame.font.SysFont(font, font_width)

player = Player("player", "Error", Colors.blue)
Globals.players.append(player)

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

info = ClientInfo()


n = Network()
info_ = n.getId()
use_data(info_)
player_id = info_.player.id

delta_time = 1/Globals.tickrate
new_info = False

start_new_thread(threaded_update, ())


#thread1 = threading.Thread(target = threaded_update, args = ())
#thread2 = threading.Thread(target = main, args = ())
#thread1.start()
#thread2.start()
main()

pygame.quit()