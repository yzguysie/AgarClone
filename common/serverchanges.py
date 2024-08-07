class ServerChanges:
    def __init__(self) -> None:        
        self.batch_id = 0
        self.objects_added = set()
        self.objects_deleted = set()
        self.players = []
        self.cells = []
        self.ejected = []
        self.viruses = []
        self.brown_viruses = []
        self.next_batch: "ServerChanges" = None