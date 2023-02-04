from __future__ import annotations
from abc import ABCMeta, abstractmethod, abstractstaticmethod
from typing import Dict, List, Tuple
from random import uniform, randint, choice, random, choices
from math import sqrt, pow

SklSlope = 0.4
AgiSlope = 0.4
SklProbabilityDrop = 0.7
AgiProbabilityDrop = 0.8


def Clamp(num: float, Min: float = 0.0, Max: float = 1.0) -> float:
    return min(Max, max(Min, num))


class Damage:
    """Class with many information about damage"""

    def __init__(self, Atk: int, Def: int, AtkDef: int, Penetrate: float, SklGap: float, IntGap: float):
        self.Atk: int = Atk
        self.Def: int = Def
        self.AtkDef: int = AtkDef
        self.Penetrate: float = Penetrate
        self.SklGap: float = SklGap
        self.IntGap: float = IntGap
        self.DamageWithPenetrate: float = max(
            self.Atk - float(self.Def * self.Penetrate), 0)


class Skill(metaclass=ABCMeta):

    @abstractstaticmethod
    def Use(User: Character, Enemy: Character, scale: int = 1, combos: int = 1, total: int = 1) -> List[Tuple[str, int]]:
        pass

    @staticmethod
    def NextAttackAndSkill(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1, lastSkill: Skill = None) -> List[Tuple[str, int]]:
        """Generate next move which can be both attack or skill

        Args:
            User (Character): The player using this function
            Enemy (Character): The enemy
            scale (float, optional): Damage scale. Defaults to 1.
            combos (int, optional): Combo count. Defaults to 1.
            total (int, optional): Total(Attack and Skill) count. Defaults to 1.
            lastSkill (Skill, optional): The skill used last move. Defaults to None.

        Returns:
            List[Tuple[str, int]]: A list of tuple, containing:
                1: the generated report
                2: the report type (0 for normal attack, 1 for skill, 2 for ending)
        """

        toReturn = []

        # Index of the skill to use, make sure the player don't use the same skill as last round
        atkSkills = User.AtkSkills
        if lastSkill:
            atkSkills = [
                skill for skill in atkSkills if not isinstance(skill, lastSkill)]

        # Has skill to use
        if atkSkills:
            atkSkill = choice(atkSkills)
            weight = User.AtkSkillWeights[User.AtkSkills.index(atkSkill)]

            # Use skill has priority
            if User.SkillProbability() > User.NAttackProbability():
                if User.ShouldUseSkill(total):
                    toReturn += choices(atkSkill, weights=weight,
                                        k=1)[0].Use(User, Enemy, scale, combos, total+1)
                elif User.ShouldUseNAttack(total):
                    toReturn += choice(User.NormalAttack).Use(User,
                                                              Enemy, scale+0.2, combos+1, total+1)

            # Use normal attack has priority
            else:
                if User.ShouldUseNAttack(total):
                    toReturn += choice(User.NormalAttack).Use(User,
                                                              Enemy, scale+0.2, combos+1, total+1)
                elif User.ShouldUseSkill(total) and User.AtkSkills:
                    toReturn += choices(atkSkill, weights=weight,
                                        k=1)[0].Use(User, Enemy, scale, combos, total+1)

        # Can only normal attack
        else:
            if User.ShouldUseNAttack(total):
                toReturn += choice(User.NormalAttack).Use(User,
                                                          Enemy, scale+0.2, combos+1, total+1)

        return toReturn

    @staticmethod
    def NextAttack(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1) -> List[Tuple[str, int]]:
        """Generate next move which can only be normal attack

        Args:
            User (Character): The player using this function
            Enemy (Character): The enemy
            scale (float, optional): Damage scale. Defaults to 1.
            combos (int, optional): Combo count. Defaults to 1.
            total (int, optional): Total(Attack and Skill) count. Defaults to 1.

        Returns:
            List[Tuple[str, int]]: A list of tuple, containing:
                1: the generated report
                2: the report type (0 for normal attack, 1 for skill, 2 for ending)
        """

        toReturn = []

        if User.ShouldUseNAttack(total):
            toReturn = choice(User.NormalAttack).Use(User,
                                                     Enemy, scale+0.2, combos+1, total+1)

        return toReturn

    @staticmethod
    def NextSkill(User: Character, Enemy: Character, scale: float = 1, combos: int = 1, total: int = 1, lastSkill: Skill = None) -> List[Tuple[str, int]]:
        """Generate next move which can be both attack or skill

        Args:
            User (Character): The player using this function
            Enemy (Character): The enemy
            scale (float, optional): Damage scale. Defaults to 1.
            combos (int, optional): Combo count. Defaults to 1.
            total (int, optional): Total(Attack and Skill) count. Defaults to 1.
            lastSkill (Skill, optional): The skill used last move. Defaults to None.

        Returns:
            List[Tuple[str, int]]: A list of tuple, containing:
                1: the generated report
                2: the report type (0 for normal attack, 1 for skill, 2 for ending)
        """

        toReturn = []

        # Index of the skill to use, make sure the player don't use the same skill as last round
        atkSkills = User.AtkSkills
        if lastSkill:
            atkSkills = [
                skill for skill in atkSkills if not isinstance(skill, lastSkill)]

        # Should use skill and has skill to use
        if User.ShouldUseSkill(total) and atkSkills:
            toReturn = choice(atkSkills).Use(
                User, Enemy, scale, combos, total+1)

        return toReturn

    @staticmethod
    def AtkInf(User: Character, Enemy: Character) -> Damage:
        """Get the Damage info

        Args:
            User (Character): _description_
            Enemy (Character): _description_

        Returns:
            Damage: Returns a Damage with many information about Damage
        """

        Atk = User.stats["攻擊"]
        Def = Enemy.stats["防禦"]/3
        AtkDef = Clamp(User.stats["攻擊"]-Enemy.stats["防禦"]/3)
        SklGap = Clamp((User.stats["技巧"]-Enemy.stats["技巧"])/350)
        IntGap = Clamp((User.stats["智力"]-Enemy.stats["智力"])/Enemy.stats["智力"])
        penetrate = 1-Clamp((SklGap*2+IntGap)/3)

        return Damage(Atk, Def, AtkDef, penetrate, SklGap, IntGap)


class Weapon:
    """A class representing a weapon"""

    def __init__(self, stats: Dict, NormalAttack: Skill, AtkSkills: List[Tuple[Skill, int]], DefSkills: List[Tuple[Skill, int]]):
        """Create a weapon

        Args:
            stats (Dict): The weapon's stats
            NormalAttack (Skill): The weapon's normal attack
            AtkSkills (List[Tuple[Skill, int]]): The weapon's attack skill 
            DefSkills (List[Tuple[Skill, int]]): The weapon's defend skill

            (The int is to represent the chance of the skill to be use, aka the weight of that skill)

        """

        self.stats: Dict = stats
        self.NormalAttack: Skill = NormalAttack
        self.AtkSkills: List[Skill] = [skill[0] for skill in AtkSkills]
        self.AtkSkillWeights: List[int] = [skill[1] for skill in AtkSkills]
        self.DefSkills: List[Skill] = [skill[0] for skill in DefSkills]
        self.DefSkillWeights: List[int] = [skill[1] for skill in DefSkills]


class StatesEnum:
    ICE = 1
    POISON = 2
    SHOCK = 3
    BOMB = 4


class State:
    def __init__(self, state: int, count: int = 0, damage: int = 0):
        """Create a state

        Args:
            state (int): The ID(StatesEnum) of the state
            count (int, optional): State count. Defaults to 0.
            damage (int, optional): Damage. Defaults to 0.
        """

        self.state = state
        self.count = count
        self.damage = damage


class CharacterState:
    def __init__(self):
        self.Ice: State = State(StatesEnum.ICE)
        self.lastIce: bool = False
        self.Poison: List[State] = []
        self.lastPoison: bool = False
        self.Shock: State = State(StatesEnum.SHOCK)
        self.lastShock: bool = False

        # Can have multiple bomb effects
        self.Bomb: List[State] = [State(StatesEnum.BOMB), ]

        self.Controlled: bool = False


class Character(metaclass=ABCMeta):

    def __init__(self, userName: str, stats: Dict, NormalAttack: Skill, AtkSkills: List[Tuple[Skill, int]], DefSkills: List[Tuple[Skill, int]], Weapons: List[Weapon]):
        """Create a Character

        Args:
            userName (str): The username of the character
            stats (Dict): The stats of the character
            NormalAttack (Skill): The normal attack of the character
            AtkSkills (List[Tuple[Skill, int]]): The attack skills of the character
            DefSkills (List[Tuple[Skill, int]]): The defend skills of the character

            (The int is to represent the chance of the skill to be use, aka the weight of that skill)

            Weapons (List[Weapon]): The weapons of the character
        """

        self.userName: str = userName
        self.stats: Dict = stats
        self.Weapons: List[List[Weapon]] = Weapons

        # Normal Attack
        self.NormalAttack: List[Skill] = [
            weapon.NormalAttack for weapon in Weapons]
        # If the weapons has normal attack(s), then overwrites the default normal attack
        self.NormalAttack = self.NormalAttack if [
            skill for skill in self.NormalAttack if skill] else [NormalAttack, ]

        # Attack skills
        self.AtkSkills: List[List[Skill]] = [[skill[0] for skill in AtkSkills], ] + \
            [weapon.AtkSkills for weapon in Weapons if weapon.AtkSkills]
        # Get rid of the Nones
        self.AtkSkills = [skill for skill in self.AtkSkills if skill]

        # The weights of the attack skills
        self.AtkSkillWeights: List[List[int]] = [[skill[1] for skill in AtkSkills], ] + \
            [weapon.AtkSkillWeights for weapon in Weapons if weapon.AtkSkillWeights]
        # Get rid of the Nones
        self.AtkSkillWeights = [
            skill for skill in self.AtkSkillWeights if skill]

        # Defend Skills
        self.DefSkills: List[List[Skill]] = [[skill[0] for skill in DefSkills], ] + \
            [weapon.DefSkills for weapon in Weapons if weapon.DefSkills]
        # Get rid of the Nones
        self.DefSkills = [skill for skill in self.DefSkills if skill]

        # The weights of the defend skills
        self.DefSkillWeights: List[List[int]] = [[skill[1] for skill in DefSkills], ] + \
            [weapon.DefSkillWeights for weapon in Weapons if weapon.DefSkillWeights]
        # Get rid of the Nones
        self.DefSkillWeights = [
            skill for skill in self.DefSkillWeights if skill]

        # Empty state
        self.State: CharacterState = CharacterState()

    def SkillProbability(self) -> float:
        """A black box"""
        # 1/3 skill and 2/3 intelligence
        x = ((self.stats["技巧"]+self.stats["智力"]*2)/3.0)/1000.0
        return x / (x + SklSlope)

    def ShouldUseSkill(self, scale: float = 1.0) -> bool:
        return random() < self.SkillProbability() * (SklProbabilityDrop**scale)

    def NAttackProbability(self) -> float:
        x = self.stats["敏捷"]/1000.0
        return x / (x + AgiSlope)

    def ShouldUseNAttack(self, scale: float = 1.0) -> bool:
        return random() < self.NAttackProbability() * (AgiProbabilityDrop**scale)

    def Attack(self, Enemy: Character) -> str:
        toReturn = []
        controlled = False
        # Ice
        if self.State.Ice.count:
            self.State.lastIce = True
            self.State.Ice.count -= 1

            self.stats["血量"] -= self.State.Ice.damage
            toReturn += [(f"{self.userName}結冰了，受到{self.State.Ice.damage}點傷害\n", 1)]

            controlled = True
        else:
            # If the player is iced last round
            if self.State.lastIce:
                self.State.lastIce = False
                toReturn += [(f"{self.userName}掙脫冰的束縛了\n", 1)]

        # Shock
        if self.State.Shock.count:
            self.State.lastShock = True
            self.State.Shock.count -= 1

            toReturn += [(f"{self.userName}被擊暈了\n", 1)]
            controlled = True
        else:
            # If the player is shocked last round
            if self.State.lastShock:
                self.State.lastShock = False
                toReturn += [(f"{self.userName}恢復意識了\n", 1)]

        # Poison
        if self.State.Poison:
            damage = 0

            # Iterate through a copy of the poison list
            for poison in self.State.Poison[:]:
                damage += poison.damage
                poison.count -= 1

                if not poison.count:
                    self.State.Poison.remove(poison)

            self.stats["血量"] -= damage

            toReturn += [(f"{self.userName}中毒了，受到{damage}點傷害\n", 1)]

        # Bomb
        # Iterate through a copy of the bomb list
        for bomb in self.State.Bomb[:]:
            if bomb.count:
                bomb.count -= 1

                if not bomb.count:
                    self.stats["血量"] -= bomb.damage
                    toReturn += [(f"{self.userName}身上的炸彈爆炸了，受到{bomb.damage}點傷害\n", 1)]

                    self.State.Bomb.remove(bomb)

        # Cannot generate moves
        if controlled:
            self.State.Controlled = True
            return toReturn
        else:
            self.State.Controlled = False

        if self.ShouldUseSkill():
            ind = randint(0, len(self.AtkSkills)-1)
            toReturn += choices(self.AtkSkills[ind],
                                weights=self.AtkSkillWeights[ind], k=1)[0].Use(self, Enemy)
        else:
            toReturn += choice(self.NormalAttack).Use(self, Enemy)

        return toReturn

    @ abstractmethod
    def Defend(self, Enemy: Character) -> str:
        return NotImplemented

    # @abstractmethod
    # def Injuried(self, Enemy: Character, AttackType: Skill):
    #     return NotImplemented
