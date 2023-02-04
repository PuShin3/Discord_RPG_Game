from Characters.Base import Character, Skill, State, CharacterState, StatesEnum, Weapon
from abc import ABCMeta, abstractmethod, abstractstaticmethod
from typing import Dict, List
from random import uniform, randint, choice, random, choices


class Run(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        if User.ShouldUseSkill():
            return f"被{User.userName}向後拉開距離躲開了攻擊\n"
        else:
            return ""


class ShootArrow(Skill):
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
            Enemy.stats["血量"] -= int(damage)
            if combos == 1:
                toReturn = f"{User.userName}攻擊，{Enemy.userName}受到了{damage}點傷害\n"
            else:
                toReturn = f"{User.userName} {combos}連擊，{Enemy.userName}受到了{damage}點傷害\n"
        Skill.NextAttackAndSkill(User, Enemy, scale, combos, total)
        return toReturn


class StrongArrow(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        damage = int((User.stats["攻擊"]) * uniform(2.0, 2.2))
        defense = Enemy.Defend(User)
        toReturn = f"{User.userName}射出了強勁的箭，"
        if defense:
            toReturn += defense
        else:
            Enemy.stats["血量"] -= int(damage)
            toReturn += f"對{Enemy.userName}造成了{damage}點傷害\n"
        toReturn += Skill.NextAttackAndSkill(User,
                                             Enemy, scale, combos, total, StrongArrow)
        return toReturn


class ExplosiveArrow(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        defend = Enemy.stats["防禦"]/3
        penetrate = min(1, max(
            0, User.stats["技巧"]-Enemy.stats["技巧"])/Enemy.stats["技巧"])
        damage = max(0, int((User.stats["攻擊"]-(defend*(1-penetrate)))
                     * uniform(1.0, 1.2)))
        defense = Enemy.Defend(User)
        toReturn = f"{User.userName}射出了會爆炸的箭，"
        if defense:
            toReturn += defense
        else:
            Enemy.stats["血量"] -= damage
            Enemy.State.Bomb.append(
                State(StatesEnum.BOMB, 2, int(damage*uniform(3.0, 5.0))))
            toReturn += f"對{Enemy.userName}造成了{damage}點傷害\n"

        toReturn += Skill.NextAttackAndSkill(User,
                                             Enemy, scale, combos, total, ExplosiveArrow)
        return toReturn


class CorrosionArrow(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        defend = Enemy.stats["防禦"]/3
        penetrate = min(1, max(
            0, User.stats["技巧"]-Enemy.stats["技巧"])/Enemy.stats["技巧"])
        trueDamage = int(User.stats["攻擊"] * uniform(0.8, 1.5))
        damage = max(0, int((User.stats["攻擊"]-(defend*(1-penetrate)))
                     * uniform(1.0, 1.2)))
        defense = Enemy.Defend(User)
        toReturn = f"{User.userName}射出了腐蝕箭，"
        if defense:
            toReturn += defense
        else:
            Enemy.stats["血量"] -= damage
            Enemy.State.Poison.append(State(StatesEnum.POISON, 3, trueDamage))
            toReturn += f"對{Enemy.userName}造成了{damage}點傷害\n"

        toReturn += Skill.NextAttackAndSkill(User,
                                             Enemy, scale, combos, total, CorrosionArrow)
        return toReturn


class ManyArrows(Skill):
    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> str:
        skillScale = 1.0
        defend = Enemy.stats["防禦"]/3
        penetrate = min(1, max(
            0, User.stats["技巧"]-Enemy.stats["技巧"]/Enemy.stats["技巧"]))
        toReturn = f"{User.userName}使出了箭失連發\n"
        for i in range(5):
            damage = max(0, int((User.stats["攻擊"]-(defend*(1-penetrate)))
                         * uniform(1.0, 2.0) * skillScale))
            defense = Enemy.Defend(User)
            if defense:
                toReturn += f"第{['一', '二', '三', '四', '五'][i]}發箭失{defense}"
            else:
                Enemy.stats["血量"] -= int(damage)
                toReturn += f"第{['一', '二', '三', '四', '五'][i]}發箭失對{Enemy.userName}造成了{damage}點傷害\n"
        toReturn += Skill.NextAttackAndSkill(User,
                                             Enemy, scale, combos, total, ManyArrows)
        return toReturn


class Archer(Character):
    def __init__(self,  userName: str, stats: Dict, weapons: List[Weapon] = []):
        Character.__init__(self, userName, stats, ShootArrow,
                           [(StrongArrow, 4), (ExplosiveArrow, 4), (CorrosionArrow, 4), (ManyArrows, 1)], [(Run, 1)], weapons)

    def Defend(self, Enemy: Character) -> str:
        if self.stats["血量"] > 0 and not self.State.Controled:
            ind = randint(0, len(self.DefSkills)-1)
            return choices(self.DefSkills[ind], weights=self.DefSkillWeights[ind], k=1)[0].Use(self, Enemy)
