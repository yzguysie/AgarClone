import pygame
from common.globals import Globals
class Player:
    def __init__(self, mode, color):
        self.id = Globals.drawable_count
        Globals.drawable_count += 1
        self.mode = mode
        self.color = color
        self.max_cells = 16
        self.min_eject_mass = 43
        
        self.target = (0, 0)
        self.cells = []
    
    def tick(self):
        for cell in self.cells:
            cell.tick()

    def draw(self):
        for cell in self.cells:
            cell.draw()

    def split(self):
        for i in range(len(self.cells)):
            if len(self.cells) < self.max_cells:
                cell = self.cells[i]
                cell.split()

    def eject_mass(self):
        for cell in self.cells:
            if cell.mass > self.min_eject_mass:
                cell.eject_mass()

    def calc_center_of_mass(self):
        try:
            center_x = 0
            center_y = 0
            weight = 0
            for cell in self.cells:
                center_x += cell.x*cell.mass
                center_y += cell.y*cell.mass
                weight += cell.mass
            return (center_x/weight, center_y/weight)
        except:
            print("divide by 0")
            return (10, 10)
                

    def update_target(self, camera, agars):
        if self.mode == "player" or self.mode == "minion":
            x, y = pygame.mouse.get_pos()
            target = (x+camera.x)*camera.scale, (y+camera.y)*camera.scale
            
        
        elif self.mode == "bot":
            nearest_agar = self.get_nearest_agar(agars)
            target = nearest_agar.x, nearest_agar.y


        else:
            target = (0, 0)

        self.target = target
        for cell in self.cells:
            cell.target = self.target
        return target
    
    def get_nearest_agar(self, agars):
        center = self.calc_center_of_mass()
        mindist = 2147483646
        #minagar = Agar(0, 0, 1, Colors.green)
        for agar in agars:
            dist_sq = (center[0]-agar.x)**2+(center[1]-agar.y)**2
            if dist_sq < mindist:
                mindist = dist_sq
                minagar = agar
        return minagar