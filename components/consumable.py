from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import color
import components.inventory
from components.base_component import BaseComponent
from exceptions import Impossible

if TYPE_CHECKING:
    from entity import Actor, Item

class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer:Actor) -> Optional[actions.Action]:
        """
        Try to return the action for this item.
        """
        action = actions.ItemAction(consumer, self.parent)
        print(f"get_action {action}")
        return action
    
    def activate(self, action: actions.ItemAction) -> None:
        """
        Invoke this items ability.
        """
        print("consumable not correctly overridden")
        raise NotImplementedError()
    
    def consume(self) -> None:
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, components.inventory.Inventory):
            inventory.items.remove(entity)
    
class HealingConsumable(Consumable):
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        print("healing consumable activate called")
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            print("healed")
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} Health!",
                color.health_recovered,
            )
            self.consume()
        else:
            print("not healed")
            raise Impossible(f"Your health is already full.")
        
        print("leaving activate after healing")