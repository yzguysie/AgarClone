import pygame
import pygame.gfxdraw
import math
import random
import time
import socket
#import threading
from _thread import *
import sys
from configparser import ConfigParser
import cProfile
import re
import copy
import pickle



from common.player import Player
from common.cell import Cell
from common.agar import Agar
from common.camera import Camera
#from common.drawable import Drawable
from common.globals import Globals
from common.virus import Virus
from common.brownvirus import BrownVirus

from common.serverinfo import ServerInfo
from common.clientinfo import ClientInfo


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

    yellow = (196, 196, 0)
    orange = (255, 127, 0)
    purple = (127, 0, 255)
    pink = (255, 16, 196)
    turquoise = (0, 255, 255)
    good_color = (32, 255, 168)
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

def new_cell(player):
    new_cell = Cell(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.player_start_mass, player.color, player)
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
    all_objs = list(all_drawable())
    all_objs.sort(key=lambda x: x.radius)
    for obj in all_objs:
        obj.draw(window, Globals.camera)

def game_tick():
    global info

    target_camera_x, target_camera_y = calc_center_of_mass(player.cells)
    target_camera_x = target_camera_x/Globals.camera.scale-width/2
    target_camera_y = target_camera_y/Globals.camera.scale-height/2
    #camera.x += (target_camera_x-camera.x)/1
    #camera.y += (target_camera_y-camera.y)/1
    Globals.camera.set_pos(target_camera_x, target_camera_y)
    Globals.camera.tick()


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



    player.update_target(Globals.camera, Globals.agars)
    for player_ in Globals.players:
        #player_.update_target(Globals.camera, Globals.agars)
        player_.tick()


    info.players = copy.deepcopy(Globals.players)
    info.cells = copy.deepcopy(Globals.cells)
    info.agars = copy.deepcopy(Globals.agars)    
    info.viruses = copy.deepcopy(Globals.viruses)
    info.brown_viruses = copy.deepcopy(Globals.brown_viruses)
    info.ejected = copy.deepcopy(Globals.ejected)

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


width, height = 1280, 720


aa_agar = True

background_color = Colors.black
font_color = Colors.green




Globals.camera = Camera()
Globals.camera.x = 0
Globals.camera.y = 0
target_scale = 105



frames = 0


ejected_to_calculate = set()



Globals.font = 'arial'
Globals.font_width = int(width/100+1)
Globals.dialogue_font = pygame.font.SysFont(Globals.font, Globals.font_width)
objects = []

pygame.display.set_caption("Agar.io Clone Server")

smoothness = 15


def get_random_color():
    colors = [Colors.red, Colors.dark_red, Colors.pink, Colors.orange, Colors.yellow, Colors.dark_green, Colors.green, Colors.purple, Colors.blue, Colors.light_blue, Colors.cyan, Colors.good_color, ]
    return colors[random.randint(0, len(colors)-1)]


smooth_fix_limit = 4

window = pygame.display.set_mode([width, height])
clock = pygame.time.Clock()

player = Player("player", get_random_color())
Globals.players.append(player)
# for i in range(bot_count):
#     Globals.players.append(Player("bot", Colors.red))
# for i in range(minion_count):
#     Globals.players.append(Player("minion", Colors.green))

player_names = ["Player", "Bot 1", "Bot 2", "Bot 3", "Bot 4", "Bot 5", "Bot 6", "Bot 7", "Bot 8", "Bot 9", "Bot 10"]

#fps_ = fps

last_time = time.time()

for i in range(int(Globals.max_agars/2)):
    Globals.agars.add(Agar(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.agar_min_mass, get_random_color()))

for i in range(int(Globals.virus_count)):
    Globals.viruses.append(Virus(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.virus_mass, Colors.green))

for i in range(int(Globals.brown_virus_count)):
    Globals.brown_viruses.append(BrownVirus(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.brown_virus_mass, Colors.brown))


playing = True
aa_text = True




info = ServerInfo()

server = "192.168.0.180"
server_ip = socket.gethostbyname(server)
print(server_ip)
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))

except socket.error as e:
    print(e)

s.listen()

print("Waiting for a connection, Server Started")



def threaded_client(conn, player_id):
    
    new_player = Player("player", get_random_color())
    Globals.players.append(new_player)
    conn.send(pickle.dumps(new_player))

    while True:
        try:
            cl_data = pickle.loads(conn.recv(4096*1024))

            if not cl_data:
                print("Disconnected")
                break
            else:
                for p in Globals.players:
                    if p.id == new_player.id:
                        p.target = cl_data.target
                        for cell in p.cells:
                            cell.target = p.target
                        if cl_data.split:
                            p.split()
                        if cl_data.eject:
                            p.eject_mass()
                        
                # print("Recieved: ", cl_data)
                # print("Sending :", info)
            
            conn.send(pickle.dumps(info))
        except:
            break
    print("Lost conection")
    conn.close()
    return


def handle_connections(useless1, useless2):
    currentPlayer = 0
    while True:
        conn, addr = s.accept()
        print("Connected to: ", addr)

        start_new_thread(threaded_client, (conn, currentPlayer))
        currentPlayer += 1

#handle_connections(1, 2)
start_new_thread(handle_connections, (1, 2))

while playing:
    start = time.time()
    #cProfile.run('game_tick()', sort='cumtime')

    Globals.cells.sort(key=lambda x: x.mass, reverse=False)
    
    window.fill(background_color)


    for p in Globals.players:
        if len(p.cells) == 0:
            if p.mode == "player":
                new_cell = Cell(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.player_start_mass, p.color, p)
            elif p.mode == "minion":
                new_cell = Cell(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.minion_start_mass, p.color, p)
            else:
                new_cell = Cell(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.bot_start_mass, p.color, p)
            Globals.cells.append(new_cell)
            p.cells.append(new_cell)
             


    if len(Globals.viruses) < Globals.virus_count:
        new_virus = Virus(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.virus_mass, Colors.green)
        while len([c for c in Globals.cells if new_virus.touching(c)]) != 0:
            new_virus = Virus(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.virus_mass, Colors.green)
        Globals.viruses.append(new_virus)

    if len(Globals.brown_viruses) < Globals.brown_virus_count:
        Globals.brown_viruses.append(BrownVirus(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.brown_virus_mass, Colors.brown))
   
    if len(Globals.agars) < Globals.max_agars:
        if frames%int(len(Globals.agars)/25000*Globals.fps+1) == 0:
            Globals.agars.add(Agar(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.agar_min_mass, get_random_color()))

    target_scale = 0
    for thing in player.cells:
        target_scale += thing.radius**(1/4)/10
       

    target_scale/= max(len(player.cells)**(1/1.5), 1)

    Globals.camera.set_scale(target_scale)

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
            if thing.mass > Globals.player_eject_min_mass and thing.mass > Globals.ejected_loss:
                thing.eject_mass()
    if pygame.key.get_pressed()[pygame.K_z]:
        player.split()
                

    game_tick()
    game_draw()


    dialogue = Globals.dialogue_font.render("Mass: " + str(int(total_mass+.5)), aa_text, font_color)
    window.blit(dialogue, (0, 0))
    dialogue = Globals.dialogue_font.render("FPS: " + str(Globals.fps_), aa_text, font_color)
    dialogue_rect = dialogue.get_rect(center=(100, 100))
    window.blit(dialogue, dialogue_rect)
    dialogue = Globals.dialogue_font.render("Cells: " + str(len(Globals.cells)), aa_text, font_color)
    dialogue_rect = dialogue.get_rect(center=(100, 125))
    window.blit(dialogue, dialogue_rect)
    dialogue = Globals.dialogue_font.render("PLAYERS: " + str(len(Globals.players)), aa_text, font_color)
    dialogue_rect = dialogue.get_rect(center=(100, 150))
    window.blit(dialogue, dialogue_rect)
    dialogue = Globals.dialogue_font.render("AGARS: " + str(len(Globals.agars)), aa_text, font_color)
    dialogue_rect = dialogue.get_rect(center=(100, 175))
    window.blit(dialogue, dialogue_rect)
    dialogue = Globals.dialogue_font.render("Ejected: " + str(len(Globals.ejected)), aa_text, font_color)
    dialogue_rect = dialogue.get_rect(center=(100, 200))
    window.blit(dialogue, dialogue_rect)

    pygame.display.flip()

   
    clock.tick(Globals.fps)
    if frames % int(Globals.fps/2) == 0:
        Globals.fps_ = round(1/(time.time()-start))
        Globals.gamespeed = min(1/Globals.fps_, 1/Globals.fps*Globals.smooth_fix_limit)
        last_time = time.time()
    frames += 1


    Globals.agars = set([agar for agar in Globals.agars if agar.id not in Globals.objects_to_delete])
    Globals.ejected = [ejected_mass for ejected_mass in Globals.ejected if ejected_mass.id not in Globals.objects_to_delete]
    Globals.cells = [cell for cell in Globals.cells if cell.id not in Globals.objects_to_delete]
    Globals.viruses = [virus for virus in Globals.viruses if virus.id not in Globals.objects_to_delete]
    Globals.brown_viruses = [brown_virus for brown_virus in Globals.brown_viruses if brown_virus.id not in Globals.objects_to_delete]
    objects = [obj for obj in objects if obj.id not in Globals.objects_to_delete]
    for cell in Globals.cells:
        if cell.mass > Globals.player_max_cell_mass:
            cell.split()
    for i in range(len(Globals.players)):
        thing = player.cells
        if len(thing) < 1:
             Globals.cells.append(Cell(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.player_start_mass, Colors.red, Globals.players[i]))
    for p in Globals.players:
        p.cells = [cell for cell in p.cells if cell.id not in Globals.objects_to_delete]

    Globals.objects_to_delete = set()


pygame.quit()
