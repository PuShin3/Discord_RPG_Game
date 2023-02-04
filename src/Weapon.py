from __future__ import annotations
from abc import ABCMeta, abstractmethod, abstractstaticmethod
from typing import Dict, List, Tuple
from random import uniform, randint, choice, random, choices
from math import sqrt, pow
from src.Characters.Base import Skill, Character


class Weapon:
    def __init__(self, stats: Dict, NormalAttack: Skill, AtkSkills: Dict[Tuple[Skill, int]], DefSkills: Dict[Tuple[Skill, int]]):
        self.stats: Dict = stats
        self.NormalAttack: Skill = NormalAttack
        self.AtkSkills: Dict[Skill] = [skill[0] for skill in AtkSkills]
        self.AtkSkillWeights: List[int] = [skill[1] for skill in AtkSkills]
        self.DefSkills: Dict[Skill] = [skill[0] for skill in DefSkills]
        self.DefSkillWeights: List[int] = [skill[1] for skill in DefSkills]
