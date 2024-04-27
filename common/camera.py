
class Camera:
    def __init__(self):
        self.pos_smoothness = 0
        self.scale_smoothness = .2

        self.scale = .15
        self.target_scale = self.scale

        self.x = 0
        self.y = 0
        self.target_x = self.x
        self.target_y = self.y

   

        self.xspeed = 0
        self.yspeed = 0

        
        self.multiplicative_friction = .8
        self.flat_friction = .1

    def tick(self):
        fps = 20
        #pass
        # if self.pos_smoothness*fps > 1:
        #     self.x += (self.target_x-self.x)/(self.pos_smoothness*fps)
        #     self.y += (self.target_y-self.y)/(self.pos_smoothness*fps)
        # else:
        #     self.x, self.y = self.target_x,self.target_y

        if (self.scale_smoothness*fps) > 1:
            self.scale += (self.target_scale-self.scale)/(self.scale_smoothness*fps)
        else:
            self.scale = self.target_scale
    
    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def set_scale(self, scale):
        self.scale = scale
        self.target_scale = scale

    def get_screen_pos(self, x, y):
        return (x/self.scale-self.x), (y/self.scale-self.y)
    
    def on_screen(self, x, y, radius):
        pass

    def get_screen_x(self, x):
        return (x/self.scale-self.x)

    def get_screen_y(self, y):
        return (y/self.scale-self.x)