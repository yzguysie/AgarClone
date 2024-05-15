from common.actor import Actor
class World:
    def __init__(self):
        self.objects = []

    def tick(self):
        for obj in self.objects:
            obj.tick()

    def draw(self):
        for obj in self.objects:
            obj.draw()
            
    def add(self, obj: Actor) -> None:
        self.objects.append(obj)
    
    def add_agar(self, agar) -> None:
        self.agars.add(agar)



