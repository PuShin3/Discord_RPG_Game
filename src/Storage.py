import operator
from typing import Dict, List, Any
from functools import reduce


class Storage:
    """
    This is a class for temporary data storage for the given user id

    Attributes:
        userID (str): The discord user id

    Return:
        A Storage object that grants you access of the user's data
    """
    __Data: Dict[str, Dict] = dict()

    def __init__(self, userID):
        self.__id = userID

        Storage.__Data.setdefault(self.__id, {
            "魔力點分配": {
                "血量": 0,
                "攻擊": 0,
                "防禦": 0,
                "體力": 0,
                "敏捷": 0,
                "智力": 0
            },
            "魔力點剩餘": 0,
            "story": None,
            "storyId": 0,
            "背包頁數": 0,
            "背包類型": 0,
            "戰報頁數": 0
        })

    def __getitem__(self, keys) -> Any:
        """Get the value from the list of keys"""
        if not isinstance(keys, tuple):
            keys = (keys,)
        return reduce(operator.getitem, keys, Storage.__Data.setdefault(self.__id, {}))

    def __setitem__(self, keys, value):
        """Get the object from the list of keys, then set it to value"""
        if not isinstance(keys, tuple):
            keys = (keys,)
        data = Storage.__Data.setdefault(self.__id, {})
        subDict = data
        for ind, key in enumerate(keys[:-1]):
            if not ind:
                subDict = data.setdefault(key, {})
                continue
            subDict = subDict.setdefault(key, {})
        subDict[keys[-1]] = value

    def contains(self, keys: List[str], value):
        """Return whether the value is in the object obtained from the keys"""
        try:
            return value in reduce(operator.getitem, keys, Storage.__Data.setdefault(self.__id, {}))
        except KeyError:
            return False
