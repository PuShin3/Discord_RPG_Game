from typing import Dict, List, Tuple
from random import uniform, randint, choice, random, choices

from src.Characters.Base import Weapon
from src.Weapons.SingleSword import SingleSword

WeaponNames: Dict[str, Weapon] = {
    "單手劍": SingleSword
}
