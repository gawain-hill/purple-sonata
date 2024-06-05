from typing import List, Reversible, Tuple
import textwrap
import color

from tcod.console import Console

class Message:
    def __init__(self, text: str, fg: Tuple[int, int, int]) -> None:
        self.plain_text = text
        self.fg = fg
        self.count = 1

    @property
    def full_text(self) -> str:
        """
        The full text of this message including the count if necessary.
        """
        if self.count > 1:
            return f"{self.plain_text} (x{self.count})"
        
        return self.plain_text
    
class MessageLog:
    def __init__(self) -> None:
        self.messages: List[Message] = []

    def add_message(
            self,
            text: str,
            fg: Tuple[int, int, int] = color.white,
            *,
            stack: bool = True
    ) -> None:
        """
        Add a message to this log.
        
        text  -- is the message text.
        fg    -- is the text color.
        stack -- if true the message will stack with the previous same message.
        """

        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(text, fg))

    def render(
            self,
            console: Console,
            x: int,
            y: int,
            width: int,
            height: int,
    ) -> None:
        """
        Renders the log to the given rectangular area.

        x -- the x component of the top left location.
        y -- the y component of the top left location.
        width -- the horizontal size of the rectangular area.
        heigh -- the vertical size of the rectangular area.
        """
        self.render_messages(console, x, y, width, height, self.messages)

    @staticmethod
    def render_messages(
        console: Console,
        x: int,
        y: int,
        width: int,
        height: int,
        messages: Reversible[Message],
    ) -> None:
        """
        Render the messages provided in reverse order (last in first out).
        """
        y_offset = height -1
        for message in reversed(messages):
            for line in reversed(textwrap.wrap(message.full_text, width)):
                console.print(x=x, y=y + y_offset, string=line, fg=message.fg)
                y_offset -= 1
                if y_offset < 0:
                    return # don't show messages without space for them