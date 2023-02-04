from typing import Dict, List, Tuple
from random import uniform, randint, choice, random, choices

from src.Characters.Base import Character
from src.Characters.Knight import Knight

CharacterNames: Dict[str, Character] = {
    "騎士": Knight
}
