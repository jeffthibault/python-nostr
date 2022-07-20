from .filter import Filters

class Subscription:
    def __init__(self, id: str, filters: Filters=None) -> None:
        self.id = id
        self.filters = filters
