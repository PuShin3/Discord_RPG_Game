from Characters.Base import Character, Skill, Weapon
from abc import ABCMeta, abstractmethod, abstractstaticmethod
from typing import Dict
from random import uniform, randint, choice, random, choices


class Fireball(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        User.stats["血量"] += 100
        return f"{User.userName}使用了魔杖回復自己100生命!\n"+Skill.NextAttack(User, Enemy, scale, combos, total)


class WandAttac(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        Enemy.stats["血量"] -= 300
        return f"{User.userName}使用魔杖用出了阿挖坦克坦拉，但實力不夠，所以{Enemy.userName}只受到了{300}點傷害\n"+Skill.NextAttack(User, Enemy, scale, combos, total)


class Wand(Weapon):
    def __init__(self):
        Weapon.__init__(self, {}, WandAttac, [(Fireball, 1)], [])
