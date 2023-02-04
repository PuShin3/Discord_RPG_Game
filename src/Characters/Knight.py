from src.Characters.Base import Character, Skill, Weapon, Damage
from abc import ABCMeta, abstractmethod, abstractstaticmethod
from typing import Dict, List
from random import uniform, randint, choice, random, choices


class SingleSlash(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        defend = Enemy.stats["防禦"]/3
        penetrate = min(1, max(
            0, User.stats["技巧"]-Enemy.stats["技巧"])/Enemy.stats["技巧"])
        damage = max(0, int((User.stats["攻擊"]-(defend*(1-penetrate)))
                     * uniform(0.8, 1.2) * scale))
        defense = Enemy.Defend(User)
        if defense:
            if combos == 1:
                toReturn = f"{User.userName}攻擊，{defense}"
            else:
                toReturn = f"{User.userName} {combos}連擊，{defense}"
        else:
            Enemy.stats["血量"] -= damage
            if combos == 1:
                toReturn = f"{User.userName}攻擊，{Enemy.userName}受到了{damage}點傷害\n"
            else:
                toReturn = f"{User.userName} {combos}連擊，{Enemy.userName}受到了{damage}點傷害\n"
        toReturn += Skill.NextAttackAndSkill(User,
                                             Enemy, scale, combos, total)
        return toReturn


class TripleSlash(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        skillScale = 1
        toReturn = f"{User.userName}使出了三連砍\n"
        for i in range(3):
            defend = Enemy.stats["防禦"]/3
            penetrate = max(
                0, User.stats["技巧"]-Enemy.stats["技巧"])/Enemy.stats["技巧"]
            damage = int((User.stats["攻擊"]-(defend*(1-penetrate)))
                         * uniform(0.8, 1.2) * skillScale)
            defense = Enemy.Defend(User)
            if defense:
                toReturn += f"第{['一', '二', '三'][i]}擊{defense}"
            else:
                Enemy.stats["血量"] -= damage
                toReturn += f"第{['一', '二', '三'][i]}擊對{Enemy.userName}造成了{damage}點傷害\n"
                skillScale += 0.2

        toReturn += Skill.NextAttack(User, Enemy,
                                     scale, combos, total)
        return toReturn


class QuadSlash(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        skillScale = 1
        toReturn = f"{User.userName}使出了垂直四方斬\n"
        for i in range(4):
            defend = Enemy.stats["防禦"]/3
            penetrate = max(
                0, User.stats["技巧"]-Enemy.stats["技巧"])/Enemy.stats["技巧"]
            damage = int((User.stats["攻擊"]-(defend*(1-penetrate)))
                         * uniform(0.8, 1.2) * skillScale)
            defense = Enemy.Defend(User)
            if defense:
                toReturn += f"第{['一', '二', '三', '四'][i]}擊{defense}"
            else:
                Enemy.stats["血量"] -= damage
                toReturn += f"第{['一', '二', '三', '四'][i]}擊對{Enemy.userName}造成了{damage}點傷害\n"
                skillScale += 0.2

        toReturn += Skill.NextAttack(User, Enemy,
                                     scale, combos, total)
        return toReturn


class WhirlSlash(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        defend = Enemy.stats["防禦"]/3
        penetrate = max(
            0, User.stats["技巧"]-Enemy.stats["技巧"])/Enemy.stats["技巧"]
        damage = int((User.stats["攻擊"]-(defend*(1-penetrate)))
                     * uniform(2.5, 2.8))
        defense = Enemy.Defend(User)
        toReturn = f"{User.userName}使出了迴旋砍，"
        if defense:
            toReturn += defense
        else:
            Enemy.stats["血量"] -= damage
            Enemy.State.Shock.count = 1
            toReturn += f"對{Enemy.userName}造成了{damage}點傷害\n"

        return toReturn


class EnhanceArmorment(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        defend = Enemy.stats["防禦"]/3
        penetrate = max(
            0, User.stats["技巧"]-Enemy.stats["技巧"])/Enemy.stats["技巧"]
        damage = int((User.stats["攻擊"]-(defend*(1-penetrate)))
                     * uniform(2.5, 2.8))
        defense = Enemy.Defend(User)
        toReturn = f"{User.userName}使地板結冰了，"
        if defense:
            toReturn += defense
        else:
            Enemy.State.Ice.count += 3
            Enemy.State.Ice.damage = damage
            toReturn += f"{Enemy.userName}被冰凍了\n"

        return toReturn


class StarburstStream(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        skillScale = 1
        toReturn = [[f"{User.userName}: 星爆...氣流斬!\n", 1]]
        for i in range(16):
            if i == 6:
                toReturn += [["克萊因：那到底是什麼技能啊？\n", 0]]
                skillScale += 0.5
            elif i == 8:
                toReturn += [["要更快\n", 0]]
                skillScale += 0.5
            elif i == 12:
                toReturn += [["還要更快!\n", 0]]
                skillScale += 0.5
            info: Damage = Skill.AtkInf(User, Enemy)
            damage = int(info.DamageWithPenetrate *
                         scale * skillScale)
            defense = Enemy.Defend(User)
            if defense:
                toReturn += [[f"第{i+1}擊{defense}", 1]]
            else:
                Enemy.stats["血量"] -= damage
                toReturn += [[f"第{i+1}擊對{Enemy.userName}造成了{damage}點傷害\n", 1]]
                skillScale += 0.2

        return toReturn


class RaiseShield(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        if User.ShouldUseSkill():
            return f"被{User.userName}使出了舉盾擋下了攻擊\n"
        else:
            return ""


class FistAtk(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        info: Damage = Skill.AtkInf(User, Enemy)
        damage = int(info.DamageWithPenetrate *
                     scale)
        defense = Enemy.Defend(User)
        toReturn = []
        if defense:
            if combos == 1:
                toReturn = [[f"{User.userName}使用拳頭揍開扁，{defense}", 1]]
            else:
                toReturn = [[f"{User.userName} {combos}連擊，{defense}", 1]]
        else:
            Enemy.stats["血量"] -= damage
            if combos == 1:
                toReturn = [
                    [f"{User.userName}使用拳頭揍開扁，{Enemy.userName}受到了{damage}點傷害\n", 0]]
            else:
                toReturn = [
                    [f"{User.userName} {combos}連擊，{Enemy.userName}受到了{damage}點傷害\n", 0]]
        nextLine = Skill.NextAttackAndSkill(User, Enemy, scale, combos, total)
        if nextLine:
            toReturn += nextLine
        return toReturn


class DoubleFist(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        skillScale = 1
        toReturn = [[f"{User.userName}使出了二連痛扁\n", 1]]
        for i in range(2):
            info: Damage = Skill.AtkInf(User, Enemy)
            damage = int(info.DamageWithPenetrate *
                         uniform(0.8, 1.2) * skillScale)
            defense = Enemy.Defend(User)
            if defense:
                toReturn += [[f"第{['一', '二'][i]}擊{defense}", 1]]
            else:
                Enemy.stats["血量"] -= damage
                toReturn += [[f"第{['一', '二'][i]}擊對{Enemy.userName}造成了{damage}點傷害\n", 1]]
                skillScale += 0.2
        nextLine = Skill.NextAttack(User, Enemy, scale, combos, total)
        if nextLine:
            toReturn += nextLine
        return toReturn


class Knight(Character):
    def __init__(self,  userName: str, stats: Dict, weapons: List[Weapon] = []):
        Character.__init__(self, userName, stats, FistAtk,
                           [(DoubleFist, 1)], [(RaiseShield, 1)], weapons)

    def Defend(self, Enemy: Character) -> str:
        if self.stats["血量"] > 0 and not self.State.Controled:
            ind = randint(0, len(self.DefSkills)-1)
            return choices(self.DefSkills[ind], weights=self.DefSkillWeights[ind], k=1)[0].Use(self, Enemy)
