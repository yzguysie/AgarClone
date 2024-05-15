from common.globals import Globals
from common.actor import Actor

class Camera:
    def __init__(self, window):
        self.window = window
        self.width, self.height = self.window.get_size()

        self.x = 0
        self.y = 0
        self.target_x = self.x
        self.target_y = self.y

        self.scale = .15
        self.target_scale = self.scale

        self.pos_smoothness = .083 # Half life (in seconds) of the difference between true position of the camera and the position from which objects are drawn. (Higher = Smoother, Lower = Snappier, more accurate)
        self.scale_smoothness = .2 # Half life (in seconds) of the difference between true scale and the scale the camera uses to draw. (Higher = Smoother, Lower = Snappier, more accurate)

    def tick(self):
        self.x += (self.target_x-self.x)/max(self.pos_smoothness*Globals.fps_, 1)
        self.y += (self.target_y-self.y)/max(self.pos_smoothness*Globals.fps_, 1)

        self.scale += (self.target_scale-self.scale)/max(self.scale_smoothness*Globals.fps_, 1)
        self.width, self.height = self.window.get_size()
    
    def set_pos(self, x, y):
        self.target_x = x
        self.target_y = y

    def set_scale(self, scale):
        self.target_scale = scale

    def get_screen_pos(self, x, y):
        return round(x/self.scale-self.x), round(y/self.scale-self.y)
    
    def on_screen(self, obj: Actor):
        raise NotImplementedError

    def get_x(self, x):
        return (x-self.width/2)*self.scale+self.x

    def get_y(self, y):
        return (y-self.height/2)*self.scale+self.y

    def get_screen_x(self, x):
        return round((x-self.x)/self.scale+self.width/2)

    def get_screen_y(self, y):
        return round((y-self.y)/self.scale+self.height/2)