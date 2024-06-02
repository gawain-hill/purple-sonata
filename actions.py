from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

class Action:
    def perform(self, engine: Engine, entity: Entity) -> None:
        """
        Perform this action with the object needed to determin its scope.

        `engine` is the scope this action is being performed in.
        `entity` is the object performing the action
        This method must be overridden by Action subclasses
        """
        raise NotImplementedError()

class EscapeAction(Action):
    def perform(self, engine: Engine, entity: Entity) -> None:
         raise SystemExit

class MovementAction(Action):
        def __init__(self, dx: int, dy: int) -> None:
             super().__init__()

             self.dx = dx
             self.dy = dy

        def perform(self, engine: Engine, entity: Entity) -> None:
            dst_x = entity.x + self.dx
            dst_y = entity.y + self.dy

            if not engine.game_map.in_bounds(dst_x, dst_y):
                return # Destination is out of bounds.
            
            if not engine.game_map.tiles["walkable"][dst_x, dst_y]:
                return # Destination not walkable.
                
            entity.move(self.dx, self.dy)