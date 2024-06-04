from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity

class Action:
    def __init__(self, entity: Entity) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """
        Returns the engine this action is scoped to.
        """
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """
        Perform this action with the object needed to determin its scope.

        This method must be overridden by Action subclasses
        """
        raise NotImplementedError()

class EscapeAction(Action):
    def perform(self) -> None:
         raise SystemExit
    
class WaitAction(Action):
    def perform(self) -> None:
        pass
    
class ActionWithDirection(Action):
    def __init__(self, entity: Entity, delta_x: int, delta_y: int) -> None:
        super().__init__(entity)

        self.delta_x = delta_x
        self.delta_y = delta_y

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
        target = self.blocking_entity
        if not target:
            return # No entity to attack
        
        print(f"You kick the {target.name}, much to its annoyance!")

class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        destination_x, destination_y = self.destination_xy

        if not self.engine.game_map.in_bounds(destination_x, destination_y):
            return # Destination is out of bounds.
        
        if not self.engine.game_map.tiles["walkable"][destination_x, destination_y]:
            return # Destination not walkable.
        
        if self.engine.game_map.get_blocking_entity_at_location(destination_x, destination_y):
            return # Destination is blocked by an entity.
            
        self.entity.move(self.delta_x, self.delta_y)
    
class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.blocking_entity:
            return MeleeAction(self.entity, self.delta_x, self.delta_y).perform()
        else:
            return MovementAction(self.entity, self.delta_x, self.delta_y).perform()