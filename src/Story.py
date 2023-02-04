"""
The type of the file is json
The story should be formatted as follows:
{
    "title": "Your title",
    "contents":[
        "name or id":{
            "content": "your Content",
            "options": [
                {
                    "option": "Your option",
                    "linkPath": "the name or id of the path you want to link",
                    "ifConditions": [
                        "the variable names you want to check(pass if exist)"
                    ],
                    "notIfConditions": [
                        "the variable names you want to check(pass if not exist)"
                    ]
                }
            ],
            "flags": [
                "variables you want to create if you got to this stage"
            ]
        }
    ],
    "initial": "name or id"
}
"""

import json
from typing import Dict, List


class Story:
    """This is a class for reading story files and format them for the user to use"""

    def __init__(self, filename: str):
        self.__filename: str = filename
        data: Dict = dict()
        with open(filename, "r", encoding="UTF-8") as f:
            data = json.load(f)
        self.__title: str = data["title"]
        self.__contents: Dict = data["contents"]
        self.__initial = data["initial"]

    @property
    def filename(self):
        return self.__filename

    @property
    def title(self):
        return self.__title

    @property
    def contents(self):
        return self.__contents

    @property
    def initial(self):
        return self.__initial

    @property
    def all_contents(self):
        datas: List = list()
        for content in self.__contents.values():
            datas.append(content["content"])
        return datas


d: Dict = dict()
Path: Dict = dict()


def printStory(s: Story, data: Dict):
    print(data["content"])
    for option in data["options"]:
        if len(option["ifConditions"]):
            for cond in option["ifConditions"]:
                if d.setdefault(cond, False):
                    print(option["option"])
        else:
            Path[option["option"]] = option["linkPath"]
            print(option["option"])
    for var in data["flags"]:
        d[var] = True


# s = Story("story.json")
# printStory(s, s.contents[s.initial])
# while 1:
#     x = input()
#     print(d)
#     printStory(s, s.contents[Path[x]])
