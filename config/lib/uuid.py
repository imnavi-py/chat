import uuid, json



class UUIDEncoder(json.JSONEncoder):
    # create by: ayoub taneh (2024-08-08)
    
    
    def default(self, obj):
        # create by: ayoub taneh (2024-08-08)
        
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)