from Characters.Base import Character, Skill, Weapon
from abc import ABCMeta, abstractmethod, abstractstaticmethod
from typing import Dict
from random import uniform, randint, choice, random, choices


class ChainAtk(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        Enemy.stats["血量"] -= 300
        toReturn = f"{User.userName}使用了鎖鏈連擊\n"
        for i in range(3):
            toReturn += f"第{['一','二','三'][i]}對{Enemy.userName}造成了{['50','100','150'][i]}點傷害\n"
        return toReturn + Skill.NextAttack(User, Enemy, scale, combos, total)


class ChainLock(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        Enemy.State.Shock.count = 4
        return f"{User.userName}使用鎖鏈擊暈了{Enemy.userName}\n"


class Chain(Weapon):
    def __init__(self):
        Weapon.__init__(self, {}, None, [], [])
