from drawable import Drawable
class World:
    def __init__(self):
        self.objects = []
        self.agars = set()

    def add(self, obj: "Drawable") -> None:
        self.objects.append(obj)
    
    def add_agar(self, agar) -> None:
        self.objects.append(agar)
        self.agars.add(agar)



