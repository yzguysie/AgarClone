class ServerChanges:
    batch_id = 0
    objects_added = set()
    objects_deleted = set()
    players = []
    cells = []
    ejected = []
    next_batch: "ServerChanges" = None