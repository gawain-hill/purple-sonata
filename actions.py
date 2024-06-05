from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING

import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item

class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """
        Returns the engine this action is scoped to.
        """
        return self.entity.parent.engine

    def perform(self) -> None:
        """
        Perform this action with the object needed to determin its scope.

        This method must be overridden by Action subclasses
        """
        raise NotImplementedError()
    
class ItemAction(Action):
    def __init__(
            self, 
            entity: Actor,
            item: Item,
            target_xy: Optional[Tuple[int, int]] = None
    ) -> None:
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Action]:
        """
        Return the actor at this actions destination
        """
        return self.engine.game_map.get_actor_at_location(*self.target_xy)
    
    @property
    def perform(self) -> None:
        """
        Invoke this items ability, this action will be given to provided context.
        """
        self.item.consumable.activate(self)

class EscapeAction(Action):
    def perform(self) -> None:
         raise SystemExit
    
class WaitAction(Action):
    def perform(self) -> None:
        pass
    
class ActionWithDirection(Action):
    def __init__(self, entity: Actor, delta_x: int, delta_y: int) -> None:
        super().__init__(entity)

        self.delta_x = delta_x
        self.delta_y = delta_y

    @property
    def target_actor(self) -> Optional[Actor]:
        """
        Returns the actor at this actions destination
        """
        return self.engine.game_map.get_actor_at_location(*self.destination_xy)

    @property
    def destination_xy(self) -> Tuple[int, int]:
        """
        Returns this actions destination.
        """
        return self.entity.x + self.delta_x, self.entity.y + self.delta_y
    
    @property
    def blocking_entity(self) -> Optional[Entity]:
        """
        Returns the entity blocking this actions destination
        """
        return self.engine.game_map.get_blocking_entity_at_location(*self.destination_xy)

    def perform(self) -> None:
        raise NotImplementedError()
    
class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.")
        
        damage = self.entity.fighter.power - target.fighter.defence

        attack_description = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_attack
        else:
            attack_color = color.enemy_attack

        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_description} for {damage} health points.", 
                attack_color,
            )
            target.fighter.health -= damage
        else:
            self.engine.message_log.add_message(
                f"{attack_description} but does no damage", 
                attack_color,
            )

class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        destination_x, destination_y = self.destination_xy

        if not self.engine.game_map.in_bounds(destination_x, destination_y):
            raise exceptions.Impossible("That way is blocked.")
        
        if not self.engine.game_map.tiles["walkable"][destination_x, destination_y]:
            raise exceptions.Impossible("That way is blocked.")
        
        if self.engine.game_map.get_blocking_entity_at_location(destination_x, destination_y):
            raise exceptions.Impossible("That way is blocked.")
            
        self.entity.move(self.delta_x, self.delta_y)
    
class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.delta_x, self.delta_y).perform()
        else:
            return MovementAction(self.entity, self.delta_x, self.delta_y).perform()