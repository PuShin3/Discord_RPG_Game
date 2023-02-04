from __future__ import annotations
from abc import ABCMeta, abstractmethod, abstractstaticmethod
from typing import Dict, List, Tuple
from random import uniform, randint, choice, random
import math
from src.Characters.Base import Character
from src.DataBase import DataBase
import time


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('%s function took %0.3f ms' %
              (f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap


def Duel(A: Character, B: Character) -> List[Tuple[str, int]]:
    toReturn: List[Tuple[str, int]] = []
    turn = 1
    count = 0

    # Simulate a duel if both people is alive and the round count is less than 100
    while A.stats["血量"] > 0 and B.stats["血量"] > 0 and count < 100:
        if turn:
            toReturn += A.Attack(B)
        else:
            toReturn += B.Attack(A)

        # Change turns
        turn = not turn

        count += 1

    if A.stats["血量"] > 0 and B.stats["血量"] > 0:
        # No winner
        toReturn += [[f"雙方大戰了100回合，不分勝負\n", 2]]
        toReturn += [[f"{A.userName}還剩{A.stats['血量']}滴血量, {B.userName}還剩{B.stats['血量']}滴血量\n", 2]]
    else:
        winner: Character = A if A.stats['血量'] > 0 else B
        loser: Character = B if A.stats['血量'] > 0 else A
        toReturn += [[f"{loser.userName}倒下了!\n", 2]]
        toReturn += [[f"{winner.userName}還有{winner.stats['血量']}滴血量\n", 2]]

    return toReturn
