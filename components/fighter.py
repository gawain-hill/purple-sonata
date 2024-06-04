from components.base_component import BaseComponent

class Figher(BaseComponent):
    def __init__(self, health: int, defence: int, power: int) -> None:
        self.max_health = health
        self._health = health
        self.defence = defence
        self.power = power

    @property
    def health(self) -> int:
        return self._health
    
    @health.setter
    def health(self, value: int) -> None:
        """
        Sets health to a value between zero and max_health
        """
        self._health = max(0, min(value, self.max_health))