from src.Characters.Base import Character, Skill, Weapon, Damage
from abc import ABCMeta, abstractmethod, abstractstaticmethod
from typing import Dict
from random import uniform, randint, choice, random, choices


class Slash(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        info: Damage = Skill.AtkInf(User, Enemy)
        damage = int(info.DamageWithPenetrate * uniform(0.8, 1.0) * scale)
        defense = Enemy.Defend(User)
        toReturn = []
        if defense:
            if combos == 1:
                toReturn = [[f"{User.userName}攻擊，{defense}", 1]]
            else:
                toReturn = [[f"{User.userName} {combos}連擊，{defense}", 1]]
        else:
            Enemy.stats["血量"] -= damage
            if combos == 1:
                toReturn = [
                    [f"{User.userName}攻擊，{Enemy.userName}受到了{damage}點傷害\n", 0]]
            else:
                toReturn = [
                    [f"{User.userName} {combos}連擊，{Enemy.userName}受到了{damage}點傷害\n", 0]]
        nextLine = Skill.NextAttackAndSkill(User, Enemy, scale, combos, total)
        if nextLine:
            toReturn += nextLine
        return toReturn


class TripleSlash(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        skillScale = 1
        info: Damage = Skill.AtkInf(User, Enemy)
        toReturn = [[f"{User.userName}使出了三連砍\n", 1]]
        for i in range(3):
            damage = int(info.DamageWithPenetrate *
                         uniform(0.8, 1.2) * skillScale)
            defense = Enemy.Defend(User)
            if defense:
                toReturn += [[f"第{['一', '二', '三'][i]}擊{defense}", 1]]
            else:
                Enemy.stats["血量"] -= damage
                toReturn += [[f"第{['一', '二', '三'][i]}擊對{Enemy.userName}造成了{damage}點傷害\n", 1]]
                skillScale += 0.2

        return toReturn


class SingleSword(Weapon):
    def __init__(self):
        Weapon.__init__(self, {}, Slash, [(TripleSlash, 1)], [])
