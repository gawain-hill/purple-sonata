https://www.rogueliketutorials.com/tutorials/tcod/v2/

Current location:
https://www.rogueliketutorials.com/tutorials/tcod/v2/part-8/

Complete but with errors

Traceback (most recent call last):
  File "main.py", line 66, in main
    engine.event_handler.handle_events(event)
  File "D:\github.com\gawain-hill\purple-sonata\input_handlers.py", line 45, in handle_events
    self.handle_action(self.dispatch(event))
  File "D:\github.com\gawain-hill\purple-sonata\input_handlers.py", line 88, in handle_action
    if super().handle_action(action):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\github.com\gawain-hill\purple-sonata\input_handlers.py", line 60, in handle_action
    action.perform()
    ^^^^^^^^^^^^^^
  File "D:\github.com\gawain-hill\purple-sonata\actions.py", line 84, in perform
    self.item.consumable.activate(self)
  File "D:\github.com\gawain-hill\purple-sonata\components\consumable.py", line 53, in activate
    self.consume()
  File "D:\github.com\gawain-hill\purple-sonata\components\consumable.py", line 36, in consume
    inventory.items.remove(entity)
ValueError: list.remove(x): x not in list