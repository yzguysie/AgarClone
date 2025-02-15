import pygame
# import pygame.gfxdraw
import math
import random
import time
import socket
import threading
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
from common.player import Player
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


def game_tick():
    global info


    #Bot AI (I think idk I wrote this like 2 yrs ago)
    # for bot in players:
    #     if bot != players[player]: #Make sure not to control player, only bots
    #         for cell in bot:
    #             target_cell = cell.target
    #             #Bots will split for their target if they can, (only if they are in two or less pieces - should add this, also why is this done for each cell wtf)
                
    #             if target_cell.mass*2.6 < cell.mass and target_cell.ID not in objects_to_delete:
    #                     if (cell.x-target_cell.x)**2+(cell.y-target_cell.y)**2 < cell.radius**2*2:
    #                         for bruh in bot:
    #                                 bruh.split()
    #                         break

    
    all_objs = list(all_drawable(cells_ = False))
    for thing in all_objs:
        thing.tick()

    #player.update_target(Globals.camera, Globals.agars) # Server player has to update, clients do elsewhere
    for player_ in Globals.players:
        if player_.mode == Player.BOT:
            player_.update_target(Globals.camera, Globals.agars)
        player_.tick()


    info.players = Globals.players
    info.cells = Globals.cells
    info.agars = Globals.agars 
    info.viruses = Globals.viruses
    info.brown_viruses = Globals.brown_viruses
    info.ejected = Globals.ejected


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
        #Globals.objects_added.add(new_virus)
    
    if obj == "brown virus":
        new_brown_virus = BrownVirus(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.brown_virus_mass, Colors.brown)
        count = 0
        while len([c for c in Globals.cells if new_brown_virus.touching(c)]) != 0 and count < 1000:
            new_brown_virus = BrownVirus(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.brown_virus_mass, Colors.brown)
            count += 1
        Globals.brown_viruses.append(new_brown_virus)
        #Globals.objects_added.add(new_brown_virus)


# def display_leaderboard(window, size: int, spacing: int, aa_text: bool = True) -> None:
#     screen_width, screen_height = window.get_size()
#     font_color = Colors.green
#     leaderboard = get_leaderboard(size)
#     dialogue = Globals.dialogue_font.render('Leaderboard', aa_text, font_color)
#     window.blit(dialogue, (screen_width-screen_width/10, screen_height/20)) 
#     for i in range(len(leaderboard)):
#         name = leaderboard[i]
#         dialogue = Globals.dialogue_font.render(f'{i+1}. {name}', aa_text, font_color)
#         window.blit(dialogue, (screen_width-screen_width/10, spacing*(i+1)+screen_height/20)) 

# def get_leaderboard(size: int) -> list:
#     leaderboard = []
#     Globals.players.sort(key=lambda x: x.mass(), reverse=True)
#     for player in Globals.players:
#         if len(leaderboard) < size:
#             leaderboard.append(player.name)
#     return leaderboard

def threaded_client(conn, player_id):
    #global changes

    connected.append(conn)
    changes_to_send[player_id] = None # FIXME Could cause last change to be doubled on client (Idk bruh fml)


    client_player = Player(Player.PLAYER, f"player {player_id}", get_random_color())
    for i in range(Globals.minion_count):
        new_minion = Player(Player.MINION, f"{client_player.name}'s minion {i+1}", Colors.green)
        if Globals.minion_count == 1:
            new_minion.name = f"{client_player.name}'s minion"
        new_minion.master_id = client_player.ID
        Globals.players.append(new_minion)
    Globals.players.append(client_player)
    info.player = client_player
    conn.send(pickle.dumps(info))

    while True:
        try:
            cl_data = pickle.loads(conn.recv(4*1024*1024))

            if not cl_data:
                print("Disconnected from ", conn)
                break
            else:
                for p in Globals.players:
                    if p.ID == client_player.ID:
                        p.target = cl_data.target
                        for cell in p.cells:
                            cell.target = p.target
                        if cl_data.split:
                            p.split()
                        if cl_data.eject:
                            p.eject_mass()
                    if p.master_id and p.master_id == client_player.ID:
                        p.target = cl_data.minion_target
                        for cell in p.cells:
                            cell.target = cl_data.minion_target
                        if cl_data.minion_split:
                            p.split()
                        if cl_data.minion_eject:
                            p.eject_mass()                
                #time.sleep(.1)
                with lock:
                    bytes_to_send = pickle.dumps((changes_to_send[player_id]))
                    changes_to_send[player_id] = None
                conn.send(bytes_to_send)
                
        except Exception as e:
            print(f'Exception {e} in threaded_client with player {client_player.name}')
            break

    print("Lost conection to ", conn)
    connected.remove(conn)
    conn.close()
    Globals.players.remove(client_player)
    # Need to remove list b/c cant edit list while iterating it
    to_remove = []
    for player in Globals.players:
        if player.master_id and player.master_id == client_player.ID:
            to_remove.append(player)

    for player in to_remove:
        Globals.players.remove(player)
            
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

    clock = pygame.time.Clock()

    Globals.smooth_fix_limit = 3

    for i in range(Globals.bot_count):
        Globals.players.append(Player(Player.BOT, f"bot {i+1}", Colors.red))

    #fps_ = fps

    last_time = time.time()

    for _ in range(int(Globals.virus_count)):
        create_new_object("virus")

    for _ in range(int(Globals.brown_virus_count)):
        create_new_object("brown virus")

    playing = True

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
    Globals.frames = 0
    playing = True
    while playing:
        slots = Globals.max_agars - len(Globals.agars)
        spawn_rate = 10
        placeholder = int(max(1, len(Globals.agars)/max(slots, 1)*Globals.tickrate/spawn_rate))

        #changes.objects_added = set()
        start = time.time()

        Globals.cells.sort(key=lambda x: x.mass, reverse=False)

        for p in Globals.players:
            if len(p.cells) == 0:
                if p.mode == Player.PLAYER:
                    #FIXME - make cells never spawn on viruses or in other cells
                    if len(Globals.ejected) > 0:
                        e = Globals.ejected[0]
                        Globals.objects_to_delete.add(e.ID)
                        new_cell = Cell(e.x, e.y, Globals.player_start_mass, p.color, p)
                    else:
                        new_cell = Cell(random.randint(-Globals.border_width, Globals.border_width), random.randint(-Globals.border_height, Globals.border_height), Globals.player_start_mass, p.color, p)
                elif p.mode == Player.MINION:
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
            if Globals.frames % placeholder == 0:
                create_new_object("agar")


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
                break
 
        game_tick()

        Globals.agars = set([agar for agar in Globals.agars if agar.ID not in Globals.objects_to_delete])
        Globals.ejected = [ejected_mass for ejected_mass in Globals.ejected if ejected_mass.ID not in Globals.objects_to_delete]
        Globals.cells = [cell for cell in Globals.cells if cell.ID not in Globals.objects_to_delete]
        Globals.viruses = [virus for virus in Globals.viruses if virus.ID not in Globals.objects_to_delete]
        Globals.brown_viruses = [brown_virus for brown_virus in Globals.brown_viruses if brown_virus.ID not in Globals.objects_to_delete]
        
        for p in Globals.players:
            p.cells = [cell for cell in p.cells if cell.ID not in Globals.objects_to_delete]

        current_changes = ServerChanges()

        current_changes.objects_deleted = Globals.objects_to_delete
        current_changes.objects_added = Globals.objects_added
        Globals.objects_to_delete = set()
        Globals.objects_added = set()

        current_changes.cells = Globals.cells
        current_changes.players = Globals.players
        current_changes.ejected = Globals.ejected
        current_changes.viruses = Globals.viruses
        current_changes.brown_viruses = Globals.brown_viruses
        if last_change:
            last_change.next_batch = current_changes
        last_change = current_changes
        #changes = current_changes
        with lock:
            for p in changes_to_send:
                if not changes_to_send[p]:
                    changes_to_send[p] = last_change # FIXME Here is the issue: I think when you make changes to send for a player a reference to last_change, when last_change is reassigned so is the player's changes. If you make a copy, the next batch will never be made

 
        clock.tick(Globals.tickrate)

        Globals.frames += 1
        Globals.fps_ = round(1/(time.time()-start))
        Globals.gamespeed = min(1/Globals.fps_, 1/Globals.tickrate*Globals.smooth_fix_limit)
        
lock = threading.Lock()

connected = []
changes_to_send: dict[int, ServerChanges] = {}
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
info = ServerInfo()
#cProfile.run('main()', sort='cumtime')
main()
pygame.quit()