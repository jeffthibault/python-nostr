from .filter import Filters

class Subscription:
    def __init__(self, id: str, filters: Filters) -> None:
        if not isinstance(id, str):
            raise TypeError("Argument 'id' must be of type str")
        self.id = id
        self.filters = filters

    def to_json_object(self):
        return { 
            "id": self.id, 
            "filters": self.filters.to_json_array() 
        }
