from __future__ import annotations

from typing import Callable, Optional, Tuple, TYPE_CHECKING

import tcod
from tcod.console import Console
from tcod.event import KeyDown, MouseButtonDown

from actions import Action, BumpAction, WaitAction, PickupAction, DropItem

import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Item

CONFIRM_KEYS = {
    tcod.event.KeySym.RETURN
}

CURSOR_Y_KEYS = { 
    tcod.event.KeySym.UP: -1,
    tcod.event.KeySym.DOWN: 1,
    tcod.event.KeySym.PAGEUP: -1,
    tcod.event.KeySym.PAGEDOWN: 1,
}

MOVE_KEYS = {
    # Arrow keys.
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.INSERT: (-1, -1),
    tcod.event.KeySym.DELETE: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),
}

WAIT_KEYS = {
    tcod.event.KeySym.PERIOD,
}

class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> None:
        self.handle_action(self.dispatch(event))

    def handle_action(self, action: Optional[Action]) -> bool:
        """
        Handle actions returned from event methods.

        Returns True if the action will advance a turn.
        """
        if action is None:
            return False
        
        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False #No one gets a turn
        
        self.engine.handle_enemy_turns()
        self.engine.update_fov()
        return True

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y
    
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()
    
    def on_render(self, console: tcod.console.Console) -> None:
        self.engine.render(console)

class AskUserEventHandler(EventHandler):
    """
    Handles user input for actions which require special input.
    """

    def handle_action(self, action: Optional[Action]) -> bool:
        if super().handle_action(action):
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return True
        return False
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """
        By default any key exits this input handler.
        """
        if event.sym in {
            tcod.event.KeySym.LSHIFT,
            tcod.event.KeySym.RSHIFT,
            tcod.event.KeySym.LCTRL,
            tcod.event.KeySym.RCTRL,
            tcod.event.KeySym.LALT,
            tcod.event.KeySym.RALT,
        }:
            return None
        
        return self.on_exit()
    
    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
        """
        By default any mouse click exits this input handler.
        """
        self.on_exit()
    
    def on_exit(self) -> Optional[Action]:
        """
        Called when the user is trying to exit or cancel an action.

        By default this returns to the main event handler.
        """
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return None

class InventoryEventHandler(AskUserEventHandler):
    """
    This handler lets the user select an item.

    What happens then depends on the subclass.
    """

    TITLE = "<missing title>"

    def on_render(self, console: tcod.console.Console) -> None:
        """
        Render an inventory menu, which displays the items, and the letter to select them
        will move to a diffirent position based on where the player is located so the player can
        always see where they are. 
        """
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        height = number_of_items_in_inventory + 2

        if height <= 3:
            height = 3
        
        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg = (0, 0, 0),
        )

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                console.print(x + 1, y + i + 1, f"({item_key}) {item.name}")
        else:
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", color.invalid)
                return None
            
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """
        Called when the user selects a valid item.
        """
        raise NotImplementedError()

class InventoryActivateHandler(InventoryEventHandler):
    """
    Handle using an inventory item.
    """
    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """
        Return the action for the selected item.
        """
        return item.consumable.get_action(self.engine.player)
    
class InventoryDropHandler(InventoryEventHandler):
    """
    Handle dropping an inventory item.
    """
    TITLE = "Select an item to drop"

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """
        Drop this item
        """
        return DropItem(self.engine.player, item)

class SelectIndexHandler(AskUserEventHandler):
    """
    Handles asking the user for a index on the map.
    """
    def __init__(self, engine: Engine) -> None:
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: Console) -> None:
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.rgb["bg"][x, y] = color.white
        console.rgb["fg"][x, y] = color.red
    
    def ev_keydown(self, event: KeyDown) -> Action | None:
        key = event.sym
        if key in MOVE_KEYS:
            modifer = 1 # Holding modifer will move further each step
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifer *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifer *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifer *= 20   

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifer
            y += dy * modifer
            # Clamp cursor to map size
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))             
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)
    
    def ev_mousebuttondown(self, event: MouseButtonDown) -> Action | None:
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)
    
    def on_index_selected(self, x: int, y: int) -> Action | None:
        raise NotImplementedError()

class SingleRangedAttackHandler(SelectIndexHandler):
    """
    Handles targeting a single enemy
    """
    def __init__(
            self, 
            engine: Engine,
            callback: Callable[[Tuple[int, int]], Action | None],
    ) -> None:
        super().__init__(engine)
        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Action | None:
        return self.callback((x, y))

class AreaRangedAttackHandler(SelectIndexHandler):
    """
    Handles targeting an area within a given radius.
    Any entity withing the area will be affected
    """
    def __init__(
        self, 
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Action | None],
    ) -> None:
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self, console: Console) -> None:
        super().on_render(console)
        x, y = self.engine.mouse_location

        console.draw_frame(
            x=x - self.radius -1,
            y=y - self.radius - 1,
            width=self.radius ** 2,
            height=self.radius ** 2,
            fg = color.red,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Action | None:
        return self.callback((x, y))

class LookHandler(SelectIndexHandler):
    def on_index_selected(self, x: int, y: int) -> Action | None:
        self.engine.event_handler = MainGameEventHandler(self.engine)

class MainGameEventHandler(EventHandler): 
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None
        key = event.sym
        player = self.engine.player

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        elif key == tcod.event.KeySym.ESCAPE:
            raise SystemExit()
        elif key == tcod.event.KeySym.v:
            self.engine.event_handler = HistroyViewer(self.engine)
        elif key == tcod.event.KeySym.g:
            action = PickupAction(player)
        elif key == tcod.event.KeySym.i:
            self.engine.event_handler = InventoryActivateHandler(self.engine)
        elif key == tcod.event.KeySym.d:
            self.engine.event_handler = InventoryDropHandler(self.engine)
        elif key == tcod.event.KeySym.SLASH:
            self.engine.event_handler = LookHandler(self.engine)

        return action

class GameOverEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        if event.sym == tcod.event.KeySym.ESCAPE:
            raise SystemExit()
    
class HistroyViewer(EventHandler):
    """
    Print the history on a larger window which can be navigated.
    """
    def __init__(self, engine: Engine) -> None:
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console) # Draw the main state as the background.
        log_console = tcod.console.Console(console.width -6, console.height - 6)

        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(0, 0, log_console.width, 1, "┤Message history├", alignment=tcod.constants.CENTER)

        # Render the message log using the cursor paramater.
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor +1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length -1
            elif adjust > 0 and self.cursor == self.log_length -1:
                # Same with bottom to top movement
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length -1))
        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0 # Move directly to the top message
        elif event.sym == tcod.event.KeySym.END:
            self.cursor = self.log_length -1 # Move directly to the last message
        else: # Any other key sent to main game state
            self.engine.event_handler = MainGameEventHandler(self.engine)