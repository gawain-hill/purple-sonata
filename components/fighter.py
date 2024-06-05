from __future__ import annotations
from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from render_order import RenderOrder
from input_handlers import GameOverEventHandler
import color

if TYPE_CHECKING:
    from entity import Actor

class Fighter(BaseComponent):
    parent: Actor

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
        if self._health <= 0 and self.parent.ai:
            self.die()

    def die(self) -> None:
        if self.engine.player is self.parent:
            death_message = "You died!"
            deth_message_color = color.player_die
            self.engine.event_handler = GameOverEventHandler(self.engine)
        else:
            death_message = f"{self.parent.name} is dead!"
            deth_message_color = color.enemy_die

        self.parent.char = "%"
        self.parent.color = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(
            death_message,
            deth_message_color
        )

    def heal(self, amount: int) -> int:
        if self.health == self.max_health:
            return 0
        
        new_health = self.health + amount

        if new_health > self.max_health:
            new_health = self.max_health

        amount_recovered = new_health - self.health
        return amount_recovered
    
    def damage(self, amount: int) -> None:
        self.health -= amount