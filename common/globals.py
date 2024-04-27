from common.camera import Camera
from configparser import ConfigParser
class Globals:
    drawable_count = 0
    player_min_mass = 43
    objects_to_delete = set()
    camera = Camera()
    fps = 30
    fps_ = 30
    gamespeed = 1/fps
    border_width = 500
    border_height = 500
    agars = set()
    cells = []
    ejected = []
    viruses = []
    brown_viruses = []
    players = []
    smooth_fix_limit = 4
    player_decay_rate = .05
    player_max_cells = 16
    player_split_min_mass = 43
    player_speed = 1
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
