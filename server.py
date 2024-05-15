import pygame
import pygame.gfxdraw
import math
import random
import time
import socket
#import threading
from _thread import *
import sys
# from configparser import ConfigParser
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
from common.serverchanges import ServerChanges

from common.clientinfo import ClientInfo
from common.colors import Colors

"""
Todo:
optimize game
make it so when one cell increases mass, camera moves smoothly
idk
"""
def get_random_color():
    colors = [Colors.red, Colors.dark_red, Colors.pink, Colors.orange, Colors.yellow, Colors.dark_green, Colors.green, Colors.purple, Colors.blue, Colors.light_blue, Colors.cyan, Colors.good_color, ]
    return colors[random.randint(0, len(colors)-1)]

def game_draw(window, player):
    target_camera_x, target_camera_y = player.calc_center_of_mass()
    Globals.camera.set_pos(target_camera_x, target_camera_y)
    Globals.camera.tick()
    all_objs = list(all_drawable())
    all_objs.sort(key=lambda x: x.radius)
    for obj in all_objs:
        obj.draw(window, Globals.camera)

def game_tick():
    global info


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

    
    all_objs = list(all_drawable(cells_ = False))
    for thing in all_objs:
        thing.tick()

    player.update_target(Globals.camera, Globals.agars) # Server player has to update, clients do elsewhere
    for player_ in Globals.players:
        if player_.mode != "player":
            player_.update_target(Globals.camera, Globals.agars)
        player_.tick()


    info.players = (Globals.players)
    info.cells = (Globals.cells)
    info.agars = (Globals.agars)    
    info.viruses = (Globals.viruses)
    info.brown_viruses = (Globals.brown_viruses)
    info.ejected = (Globals.ejected)
    # info.players = copy.deepcopy(Globals.players)
    # info.cells = copy.deepcopy(Globals.cells)
    # info.agars = copy.deepcopy(Globals.agars)    
    # info.viruses = copy.deepcopy(Globals.viruses)
    # info.brown_viruses = copy.deepcopy(Globals.brown_viruses)
    # info.ejected = copy.deepcopy(Globals.ejected)

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

def create_new_object(obj: str):
    if obj == "agar":
        new_agar = Agar(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.agar_min_mass, get_random_color())
        Globals.agars.add(new_agar)
        Globals.objects_added.add(new_agar)

    if obj == "virus":
        new_virus = Virus(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.virus_mass, Colors.green)
        count = 0
        while len([c for c in Globals.cells if new_virus.touching(c)]) != 0 and count < 1000:
            new_virus = Virus(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.virus_mass, Colors.green)
            count += 1
        Globals.viruses.append(new_virus)
        Globals.objects_added.add(new_virus)
    
    if obj == "brown virus":
        new_brown_virus = BrownVirus(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.brown_virus_mass, Colors.brown)
        count = 0
        while len([c for c in Globals.cells if new_brown_virus.touching(c)]) != 0 and count < 1000:
            new_brown_virus = BrownVirus(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.brown_virus_mass, Colors.brown)
            count += 1
        Globals.brown_viruses.append(new_brown_virus)
        Globals.objects_added.add(new_brown_virus)

def display_metrics(window, distance: int, aa_text: bool = True):
    font_color = Colors.green
    dialogue = Globals.dialogue_font.render("Fps: " + str(Globals.fps_), aa_text, font_color)
    window.blit(dialogue, (0, 0))
    # dialogue = Globals.dialogue_font.render("Mass: " + str(int(total_mass+.5)), aa_text, font_color)
    # window.blit(dialogue, (0, distance*2))
    dialogue = Globals.dialogue_font.render("Players: " + str(len(Globals.players)), aa_text, font_color)
    window.blit(dialogue, (0, distance*4))
    dialogue = Globals.dialogue_font.render("Cells: " + str(len(Globals.cells)), aa_text, font_color)
    window.blit(dialogue, (0, distance*5))
    dialogue = Globals.dialogue_font.render("Agars: " + str(len(Globals.agars)), aa_text, font_color)
    window.blit(dialogue, (0, distance*6))
    dialogue = Globals.dialogue_font.render("Ejected: " + str(len(Globals.ejected)), aa_text, font_color)
    window.blit(dialogue, (0, distance*7))

def threaded_client(conn, player_id):
    #global changes

    connected.append(conn)
    changes_to_send[player_id] = None # FIXME Could cause last change to be doubled on client (Idk bruh fml)


    new_player = Player("player", get_random_color())
    Globals.players.append(new_player)
    info.player = new_player
    conn.send(pickle.dumps(info))

    while True:
        try:
            cl_data = pickle.loads(conn.recv(4*1024*1024))

            if not cl_data:
                print("Disconnected from ", conn)
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
                conn.send(pickle.dumps((changes_to_send[player_id])))
                changes_to_send[player_id] = None
        except:
            break

    print("Lost conection to ", conn)
    connected.remove(conn)
    conn.close()
    Globals.players.remove(new_player)
    del changes_to_send[player_id]
    return

def handle_connections():
    global s
    currentPlayer = 0
    while True:
        conn, addr = s.accept()
        print("Connected to: ", addr)

        start_new_thread(threaded_client, (conn, currentPlayer))
        currentPlayer += 1

def main():
    global changes_to_send  #, changes
    pygame.init()


    # config = ConfigParser()

    # # parse existing file
    # config.read('common/agar.ini')

    aa_agar = True

    background_color = Colors.black
    font_color = Colors.green

    screen_width, screen_height = 1280, 720
    screen_fullscreen : bool = False
    window = pygame.display.set_mode([screen_width, screen_height], pygame.RESIZABLE)
    pygame.display.set_caption("Agar.io Clone Server")
    clock = pygame.time.Clock()


    Globals.camera = Camera(window)


    Globals.font = 'arial'
    Globals.font_width = int(screen_width/100+1)
    Globals.dialogue_font = pygame.font.SysFont(Globals.font, Globals.font_width)

    Globals.smooth_fix_limit = 3

    Globals.players.append(player)
    for i in range(Globals.bot_count):
        Globals.players.append(Player("bot", Colors.red))
    for i in range(Globals.minion_count):
        Globals.players.append(Player("minion", Colors.green))

    player_names = ["Player", "Bot 1", "Bot 2", "Bot 3", "Bot 4", "Bot 5", "Bot 6", "Bot 7", "Bot 8", "Bot 9", "Bot 10"]

    #fps_ = fps

    last_time = time.time()

    for _ in range(int(Globals.max_agars/2)):
        create_new_object("agar")

    for _ in range(int(Globals.virus_count)):
        create_new_object("virus")

    for _ in range(int(Globals.brown_virus_count)):
        create_new_object("brown virus")

    playing = True
    aa_text = True

    server = ""
    server_ip = socket.gethostbyname(server)
    port = 5555

    try:
        s.bind((server, port))

    except socket.error as e:
        print(e)

    s.listen()

    print("Waiting for a connection, Server Started")

    last_change = None

    #handle_connections(1, 2)
    start_new_thread(handle_connections, ())
    #global changes, screen_height, last_change
    frames = 0
    playing = True
    while playing:
        #changes.objects_added = set()
        start = time.time()

        Globals.cells.sort(key=lambda x: x.mass, reverse=False)
        
        window.fill(background_color)


        for p in Globals.players:
            if len(p.cells) == 0:
                if p.mode == "player":
                    #FIXME - make cells never spawn on viruses or in other cells
                    if len(Globals.ejected) > 0:
                        e = Globals.ejected[0]
                        Globals.objects_to_delete.add(e.id)
                        new_cell = Cell(e.x, e.y, Globals.player_start_mass, p.color, p)
                    else:
                        new_cell = Cell(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.player_start_mass, p.color, p)
                elif p.mode == "minion":
                    new_cell = Cell(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.minion_start_mass, p.color, p)
                else:
                    new_cell = Cell(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.bot_start_mass, p.color, p)
                Globals.cells.append(new_cell)
                p.cells.append(new_cell)
                


        if len(Globals.viruses) < Globals.virus_count:
            create_new_object("virus")

        if len(Globals.brown_viruses) < Globals.brown_virus_count:
            create_new_object("brown virus")
    
        if len(Globals.agars) < Globals.max_agars:
            if frames%int(len(Globals.agars)/25000/Globals.gamespeed+1) == 0:
                create_new_object("agar")

        target_scale = 0
        for thing in player.cells:
            target_scale += thing.radius**(1/4)/10
        

        target_scale/= max(len(player.cells)**(1/1.5), 1)

        Globals.camera.set_scale(target_scale*720/screen_height)

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

            if event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = window.get_size()

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
                    screen_fullscreen = not screen_fullscreen
                    if screen_fullscreen:
                        pygame.display.set_mode((0,0), pygame.FULLSCREEN)
                    else:
                        pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
                    screen_width, screen_height = window.get_size()

        if pygame.key.get_pressed()[pygame.K_e]:
            for thing in player.cells:
                if thing.mass > Globals.player_eject_min_mass and thing.mass > Globals.ejected_loss:
                    thing.eject_mass()
        if pygame.key.get_pressed()[pygame.K_z]:
            player.split()
                    
        game_tick()
        game_draw(window, player)

        display_metrics(window, 25)
        
        Globals.agars = set([agar for agar in Globals.agars if agar.id not in Globals.objects_to_delete])
        Globals.ejected = [ejected_mass for ejected_mass in Globals.ejected if ejected_mass.id not in Globals.objects_to_delete]
        Globals.cells = [cell for cell in Globals.cells if cell.id not in Globals.objects_to_delete]
        Globals.viruses = [virus for virus in Globals.viruses if virus.id not in Globals.objects_to_delete]
        Globals.brown_viruses = [brown_virus for brown_virus in Globals.brown_viruses if brown_virus.id not in Globals.objects_to_delete]
        for cell in Globals.cells:
            if cell.mass > Globals.player_max_cell_mass:
                cell.split()
        # for i in range(len(Globals.players)):
        #     thing = player.cells
        #     if len(thing) < 1:
        #          Globals.cells.append(Cell(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.player_start_mass, Colors.red, Globals.players[i]))
        for p in Globals.players:
            p.cells = [cell for cell in p.cells if cell.id not in Globals.objects_to_delete]

        current_changes = ServerChanges()

        current_changes.objects_deleted = Globals.objects_to_delete
        current_changes.objects_added = Globals.objects_added
        # current_changes.cells = copy.deepcopy(Globals.cells)
        # current_changes.players = copy.deepcopy(Globals.players) -> We only need the most recent copies anyway
        # current_changes.ejected = copy.deepcopy(Globals.ejected)
        current_changes.cells = Globals.cells
        current_changes.players = Globals.players
        current_changes.ejected = Globals.ejected
        if last_change:
            last_change.next_batch = current_changes
        last_change = current_changes
        #changes = current_changes
        for p in changes_to_send:
            if not changes_to_send[p]:
                changes_to_send[p] = last_change # FIXME Here is the issue: I think when you make changes to send for a player a reference to last_change, when last_change is reassigned so is the player's changes. If you make a copy, the next batch will never be made
        
        Globals.objects_to_delete = set()
        Globals.objects_added = set()
 
        clock.tick(Globals.tickrate)
        pygame.display.flip()

        Globals.frames += 1
        Globals.fps_ = round(1/(time.time()-start))
        Globals.gamespeed = min(1/Globals.fps_, 1/Globals.tickrate*Globals.smooth_fix_limit)
        

connected = []
changes_to_send: dict[int, ServerChanges] = {}
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
player = Player("player", get_random_color())
info = ServerInfo()
#changes = ServerChanges()
#cProfile.run('main()', sort='cumtime')
main()
pygame.quit()