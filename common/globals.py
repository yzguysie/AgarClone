from configparser import ConfigParser
import pygame
pygame.font.init()
class Globals:
    font = 'arial'
    font_width = int(1280/100+1)
    dialogue_font = pygame.font.SysFont(font, font_width)
    drawable_count = 0
    objects_to_delete = set()
    objects_added = set()
    camera = None
    agars = set()
    cells = []
    ejected = []
    viruses = []
    brown_viruses = []
    players = []
    smooth_fix_limit = 4
    config = ConfigParser()
    frames = 0

    # parse existing file
    config.read('common/agar.ini')

    # read values from a section
    tickrate = config.getint('settings', 'tickrate')
    fps = config.getint('settings', 'fps')
    fps_ = fps
    gamespeed = 1/tickrate
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
    virus_split_mass = config.getint('settings', 'virus_split_mass')

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

    agar_min_mass = config.getint('settings', 'agar_min_mass')
    agar_max_mass = config.getint('settings', 'agar_max_mass')
    max_agars = config.getint('settings', 'max_agars')

    ejected_size = config.getint('settings', 'ejected_size')
    ejected_loss = config.getint('settings', 'ejected_loss')
    ejected_speed = config.getint('settings', 'ejected_speed')

    bot_count = config.getint('settings', 'bot_count')
    bot_start_mass = config.getint('settings', 'bot_start_mass')

    minion_count = config.getint('settings', 'minion_count')
    minion_start_mass = config.getint('settings', 'minion_start_mass')

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
