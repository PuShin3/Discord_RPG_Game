from __future__ import annotations
import interactions
from typing import Tuple, List, Dict
from functools import cmp_to_key

from src.DataBase import DataBase
from src.Storage import Storage


def sortByEquipAndName(x: Dict, y: Dict) -> bool:
    if x["裝備"]:
        return True
    if y["裝備"]:
        return False
    return x["名稱"] < y["名稱"]


class UI:
    @staticmethod
    def createSkillMenuEmbed(ctx: interactions.CommandContext, db: DataBase) -> interactions.Embed:
        userId = str(ctx.user.id)
        embed = interactions.Embed(
            title="玩家檔案",
            color=0xFFA500
        )

        embed.set_author(f"{ctx.user.username}-skillpoint",
                         icon_url=ctx.user.avatar_url)
        embed.set_thumbnail(ctx.user.avatar_url)
        embed.add_field(name="數值", value=f"❤️ **血量**: {db[userId]['魔力量']['血量']} (+{Storage(userId)['魔力點分配']['血量']}\n"
                        f"🔪 **攻擊**: {db[userId]['魔力量']['攻擊']} (+{Storage(userId)['魔力點分配']['攻擊']}\n"
                        f"🛡️ **防禦**: {db[userId]['魔力量']['防禦']} (+{Storage(userId)['魔力點分配']['防禦']}\n"
                        f"🏃 **體力**: {db[userId]['魔力量']['體力']} (+{Storage(userId)['魔力點分配']['體力']}\n"
                        f"🛹 **敏捷**: {db[userId]['魔力量']['敏捷']} (+{Storage(userId)['魔力點分配']['敏捷']}\n"
                        f"🔧 **技巧**: {db[userId]['魔力量']['技巧']} (+{Storage(userId)['魔力點分配']['技巧']}\n"
                        f"🧠 **智力**: {db[userId]['魔力量']['智力']} (+{Storage(userId)['魔力點分配']['智力']}\n")
        embed.add_field(name="可分配魔力量", value=f"{Storage(userId)['魔力點剩餘']}")
        return embed

    @staticmethod
    def createSkillMenuComponent() -> interactions.SelectMenu:
        return interactions.SelectMenu(
            options=[
                interactions.SelectOption(
                    label="血量",
                    value="血量",
                    description="可以提升血量"
                ),
                interactions.SelectOption(
                    label="攻擊",
                    value="攻擊",
                    description="可以提升攻擊"
                ),
                interactions.SelectOption(
                    label="防禦",
                    value="防禦",
                    description="可以提升防禦"
                ),
                interactions.SelectOption(
                    label="體力",
                    value="體力",
                    description="可以提升體力"
                ),
                interactions.SelectOption(
                    label="敏捷",
                    value="敏捷",
                    description="可以提升敏捷"
                ),
                interactions.SelectOption(
                    label="技巧",
                    value="技巧",
                    description="可以提升技巧"
                ),
                interactions.SelectOption(
                    label="智力",
                    value="智力",
                    description="可以提升智力，不讓你變成智障"
                )
            ],
            placeholder="Select a ability to check",
            custom_id="skillmenu"
        )

    @staticmethod
    def createSkillDesEmbed(ctx: interactions.CommandContext, db: DataBase, value) -> interactions.Embed:
        userId = str(ctx.user.id)
        embed = interactions.Embed(title=value, color=0x00FF00)
        embed.set_author(f"{ctx.user.username}-skillpoint",
                         icon_url=ctx.user.avatar_url)
        if value == "血量":
            embed.add_field(name="描述", value="可以提升血量")
        elif value == "攻擊":
            embed.add_field(name="描述", value="可以提升攻擊")
        elif value == "防禦":
            embed.add_field(name="描述", value="可以提升防禦")
        elif value == "體力":
            embed.add_field(name="描述", value="可以提升體力")
        elif value == "敏捷":
            embed.add_field(name="描述", value="可以提升敏捷")
        elif value == "技巧":
            embed.add_field(name="描述", value="可以提升技巧")
        elif value == "智力":
            embed.add_field(name="描述", value="可以提升智力，不讓你變成智障")
        embed.add_field(
            name="可分配魔力量", value=f"  {Storage(userId)['魔力點剩餘']}", inline=True)
        embed.add_field(
            name=f"{value}", value=f"  +{db[userId]['魔力量'][value]+Storage(userId)['魔力點分配'][value]}", inline=True)
        return embed

    @staticmethod
    def createInventoryEmbed(ctx: interactions.CommandContext, db: DataBase) -> Tuple:
        userId = str(ctx.user.id)
        embed = interactions.Embed(title="玩家背包", color=0xFF0000)
        embed.set_author(f"{ctx.user.username}-inventory",
                         icon_url=ctx.user.avatar_url)
        options = []
        items = ""
        count = ""
        armor = []
        food = []
        item = []
        for item in db[userId]["背包"]:
            if item["種類"] == "裝甲武器":
                armor.append(item)
            elif item["種類"] == "食物":
                food.append(item)
            else:
                item.append(item)
        sorted(armor, key=cmp_to_key(sortByEquipAndName))
        food.sort()
        item.sort()
        for item in db[userId]["背包"]:
            items += f"{item['名稱']}\n"
            count += f"{item['數量']}\n"
            options.append(interactions.SelectOption(
                label=item['名稱'],
                value=item['名稱'],
                description=item['數量']
            ))
        embed.add_field(name="物品名稱", value=items, inline=True)
        embed.add_field(name="數量", value=count, inline=True)
        return (embed, options, )

    @staticmethod
    def createPickInventoryEmbed(ctx: interactions.CommandContext, db: DataBase, name: str) -> interactions.Embed:
        userId = str(ctx.user.id)
        embed = interactions.Embed(
            title=name, color=0x13DD66)
        embed.set_author(f"{ctx.user.username}-名稱",
                         icon_url=ctx.user.avatar_url)
        embed.add_field(name="物品名稱", value=name)
        items = [item["名稱"] for item in db[userId]["背包"]]
        embed.add_field(
            name="物品數量", value=db[userId]["背包"][items.index(name)]["數量"])
        return embed

    @staticmethod
    def createStoryComponents(ctx: interactions.CommandContext) -> List[interactions.SelectOption]:
        userId = str(ctx.user.id)
        if not Storage(userId).contains((), "storyVars"):
            Storage(userId)["storyVars"] = {}
        components: List[interactions.SelectOption] = list()
        for option in Storage(userId)["story"].contents[Storage(userId)["storyId"]]["options"]:
            show = True

            for cond in option["ifConditions"]:
                if not Storage(userId).contains(("storyVars",), cond):
                    Storage(userId)["storyVars", cond] = False
                if not Storage(userId)["storyVars"][cond]:
                    show = False
                    break

            for cond in option["notIfConditions"]:
                if not Storage(userId).contains(("storyVars",), cond):
                    Storage(userId)["storyVars", cond] = False
                if Storage(userId)["storyVars"][cond]:
                    show = False
                    break

            if show:
                components.append(
                    interactions.SelectOption(
                        label=option["option"],
                        value=option["linkPath"]
                    ))
        for flag in Storage(userId)["story"].contents[Storage(userId)["storyId"]]["flags"]:
            Storage(userId)["storyVars", flag] = True
        return components
