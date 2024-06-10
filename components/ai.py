from __future__ import annotations

import random
from typing import List, Tuple, TYPE_CHECKING

import numpy as np
import tcod

from actions import Action, BumpAction, MeleeAction, MovementAction, WaitAction
from entity import Actor

if TYPE_CHECKING:
    from entity import Actor

class BaseAI(Action):
    def perform(self) -> None:
        raise NotImplementedError()
    
    def get_path_to(self, destination_x: int, destination_y: int) -> List[Tuple[int, int]]:
        """
        Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        cost = np.array(self.entity.parent.tiles["walkable"], dtype=np.int8)
        for entity in self.entity.parent.entities:
            # Check that an entity blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position
                # A lower numberr means more enemies will crowd behind each other in hallways.
                # A higher number means enemies will take longer paths
                # in order to surround the player
                cost[entity.x, entity.y] +=10
            
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)
        pathfinder.add_root((self.entity.x, self.entity.y))
        path: List[List[int]] = pathfinder.path_to((destination_x, destination_y))[1:].tolist()
        
        return [(index[0], index[1]) for index in path]

class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a given number of turns then revert
    back If an actor occupies a tile it is randomly moving to it will attack.
    """
    def __init__(
            self, entity: Actor, 
            previous_ai: BaseAI | None, 
            turns_remaining: int
    ) -> None:
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # Revert the API back to the origional state if the effect has
        # run out
        if self.turns_remaining <= 0:
            self.engine.message_log(
                f"The {self.entity.name} is no longer confused."
            )
            self.entity.ai = self.previous_ai
        else:
            direction_x, direction_y = random.choice(
                [
                    (-1, -1),
                    (0, -1),
                    (1, -1),
                    (-1, 0),
                    (1, 0),
                    (-1, 1),
                    (0, 1),
                    (1, 1),
                ]
            )

            self.turns_remaining -= 1

            return BumpAction(self.entity, direction_x, direction_y).perform()

class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor) -> None:
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy)) # Chebshev distance.

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()
            
            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity,
                dest_x - self.entity.x, 
                dest_y - self.entity.y
            ).perform()
        
        return WaitAction(self.entity).perform()