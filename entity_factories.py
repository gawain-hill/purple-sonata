from components.ai import HostileEnemy
from components.fighter import Fighter
from components.consumable import HealingConsumable
from entity import Actor, Item

player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player", 
    ai_class=HostileEnemy,
    figher=Fighter(health=30, defence=2, power=5),
)

orc = Actor(
    char="o", 
    color=(63, 127, 63), 
    name="Orc", 
    ai_class=HostileEnemy,
    figher=Fighter(health=10, defence=0, power=3),
)

troll = Actor(
    char="T", 
    color=(0, 127, 0), 
    name="Troll", 
    ai_class=HostileEnemy,
    figher=Fighter(health=16, defence=1, power=4),
)

health_potion = Item(
    char="!",
    color=(127, 0, 255),
    name="Health Potion",
    consumable=HealingConsumable(amount=4),
)