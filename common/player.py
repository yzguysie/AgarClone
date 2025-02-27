import pygame
from common.globals import Globals
import math
class Player:
    s_next_player_id: int = 0
    PLAYER: int = 0
    BOT: int = 1
    MINION: int = 2
    def __init__(self, mode: int, name: str, color: tuple [int, int, int]):
        self.ID = Player.s_next_player_id
        Player.s_next_player_id += 1
        # TODO - Make player modes an Enum
        self.mode: int = mode
        self.name: str = name
        self.color: tuple[int, int, int] = color
        self.max_cells: int = Globals.player_max_cells
        self.min_eject_mass: int = Globals.player_eject_min_mass
        self.master_id: int = None
        self.target: tuple[float, float] = (0, 0)
        self.cells = []
    
    def tick(self) -> None:
        for cell in self.cells:
            cell.tick()
            
    def tick_client(self) -> None:
        for cell in self.cells:
            cell.tick_client()

    def draw(self, window, camera) -> None:
        for cell in self.cells:
            cell.draw(window, camera)

    def split(self) -> None:
        for i in range(len(self.cells)):
            if len(self.cells) < self.max_cells:
                cell = self.cells[i]
                cell.split()

    def eject_mass(self) -> None:
        for cell in self.cells:
            if cell.mass > self.min_eject_mass:
                cell.eject_mass()

    def get_mass(self) -> float:
        cells = [cell for cell in self.cells if cell.ID not in Globals.objects_to_delete]
        return sum(cell.mass for cell in self.cells)
            

    def calc_center_of_mass(self) -> tuple[float, float]:
        #TODO - Wtf is this blud
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
            # print("Error: Divide by 0 (Possible that client has no player)")
            return (10, 10)
                

    def update_target(self, camera, agars):
        if self.mode == Player.PLAYER or self.mode == Player.MINION:
            x, y = pygame.mouse.get_pos()
            target = (x+camera.x)*camera.scale, (y+camera.y)*camera.scale
            target = camera.get_x(x), camera.get_y(y)
            
        
        elif self.mode == Player.BOT:
            nearest_agar = self.get_nearest_obj(agars)
            target = nearest_agar.x, nearest_agar.y


        else:
            target = (0, 0)

        self.target = target
        for cell in self.cells:
            cell.target = self.target
        return target
    
    def get_nearest_obj(self, digga):
        center_x, center_y = self.calc_center_of_mass()
        mindist = self.cells[0].radius*3
        found = False
        for obj in Globals.cells:
            if obj.player != self:
                if obj.mass*1.3 < self.cells[0].mass:
                    dist = math.sqrt((center_x-obj.x)**2+(center_y-obj.y)**2)
                    if dist < mindist:
                        mindist = dist
                        near = obj
                        found = True
        if found:
            return near
        mindist = self.cells[0].radius*10
        found = False
        for obj in Globals.ejected:
            if obj.mass*1.3 < self.cells[0].mass:
                dist = math.sqrt((center_x-obj.x)**2+(center_y-obj.y)**2)
                if dist < mindist:
                    mindist = dist
                    near = obj
                    found = True
        if found:
            return near
        mindist = 2147483646
        for obj in Globals.agars:
            dist_sq = (center_x-obj.x)**2+(center_y-obj.y)**2
            if dist_sq < mindist:
                mindist = dist_sq
                minagar = obj
        return minagar
