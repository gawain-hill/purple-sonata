from __future__ import annotations
from typing import List, Tuple

import numpy as np
import tcod

from actions import Action
from components.base_component import BaseComponent

class BaseAI(Action, BaseComponent):
    def perform(self) -> None:
        raise NotImplementedError()
    
    def get_path_to(self, destination_x: int, destination_y: int) -> List[Tuple[int, int]]:
        """
        Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)
        for entity in self.entity.gamemap.entities:
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