from components.ai import HostileEnemy
from components.fighter import Fighter
from entity import Actor

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