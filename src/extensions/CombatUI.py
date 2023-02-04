from __future__ import annotations
import interactions


from src.Storage import Storage
from src.DataBase import DataBase
from src.Inventory import Inventory
from src.UI import UI
from src.Story import Story
from src.Combat import Duel
from src.Characters.Base import Character, Weapon

from src.Characters.CharacterNames import CharacterNames
from src.Weapons.WeaponNames import WeaponNames

from src.extensions.db import db
from src.extensions.db import reports

from typing import List, Dict, Tuple
import Levenshtein

statsName = ["血量", "攻擊", "防禦", "體力", "敏捷", "智力"]
armorName = ["頭盔", "胸甲", "腿甲", "鞋子", "主武器", "副武器"]

linePerPage = 20


def validPlayer(db: DataBase, nickname: str) -> bool:
    """ Check if the player is valid

    Args:
        db (DataBase): DataBase
        nickname (str): The nickname of the user

    Returns:
        bool: If the player is valid
    """

    nameList = [player["暱稱"] for player in db.getData()]
    return nickname in nameList


async def createPlayerEmbed(ctx: interactions.CommandContext, db: DataBase, nickName: str) -> interactions.Embed:
    """Create an embed for the player page

    Args:
        ctx (interactions.CommandContext): Command Context
        db (DataBase): DataBase
        nickName (str): The nickname of the player

    Returns:
        interactions.Embed: Returns an embed for the player page
    """

    # Create the embed
    embed = interactions.Embed(title=nickName, color=0xFFA500)
    embed.set_author("搜尋玩家", icon_url=ctx.user.avatar_url)
    nameList = [player["暱稱"] for player in db.getData()]

    # Check if player is valid
    if not validPlayer(db, nickName):
        embed.title = f"{nickName}-此玩家不存在"
        return embed

    ind = nameList.index(nickName)
    userId = db.getKeys()[ind]
    nameList = [item["名稱"] for item in db[userId]["背包"]["裝甲武器"]]

    # Get user
    user = await ctx.client.get_user(int(userId))

    # Get user avatar
    embed.set_thumbnail(
        url=f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png")
    embed.add_field(name="**等級**", value=db[userId]["等級"])

    # Get the stat of all the armor
    armorStats = {"血量": 0, "攻擊": 0, "防禦": 0}
    for aName in armorName:
        name = db[userId]["裝備"][aName]
        if name and db[userId]["背包"]["裝甲武器"][nameList.index(name)]["裝備"]:
            ind = nameList.index(name)
            armorStats["血量"] += db[userId]["背包"]["裝甲武器"][ind]["數值"]["血量"]
            armorStats["攻擊"] += db[userId]["背包"]["裝甲武器"][ind]["數值"]["攻擊"]
            armorStats["防禦"] += db[userId]["背包"]["裝甲武器"][ind]["數值"]["防禦"]

    # Add stat field
    embed.add_field(name="數值", value=f"❤️ **血量**: {db[userId]['狀態']['血量']+armorStats['血量']+db[userId]['魔力量']['血量']}\n"
                    f"🔪 **攻擊**: {db[userId]['狀態']['攻擊']+armorStats['攻擊']+db[userId]['魔力量']['攻擊']}\n"
                    f"🛡️ **防禦**: {db[userId]['狀態']['防禦']+armorStats['防禦']+db[userId]['魔力量']['防禦']}\n"
                    f"🏃 **體力**: {db[userId]['狀態']['體力']+db[userId]['魔力量']['體力']}\n"
                    f"🛹 **敏捷**: {db[userId]['狀態']['敏捷']+db[userId]['魔力量']['敏捷']}\n"
                    f"🔧 **技巧**: {db[userId]['狀態']['技巧']+db[userId]['魔力量']['技巧']}\n"
                    f"🧠 **智力**: {db[userId]['狀態']['智力']+db[userId]['魔力量']['智力']}\n")

    # Add armor field
    embed.add_field(name="裝備", value=f"**頭盔**: {db[userId]['裝備']['頭盔'] if db[userId]['裝備']['頭盔'] else '無'}\n"
                    f"**胸甲**: {db[userId]['裝備']['胸甲'] if db[userId]['裝備']['胸甲'] else '無'}\n"
                    f"**腿甲**: {db[userId]['裝備']['腿甲'] if db[userId]['裝備']['腿甲'] else '無'}\n"
                    f"**鞋子**: {db[userId]['裝備']['鞋子'] if db[userId]['裝備']['鞋子'] else '無'}\n"
                    f"**主武器**: {db[userId]['裝備']['主武器'] if db[userId]['裝備']['主武器'] else '無'}\n"
                    f"**副武器**: {db[userId]['裝備']['副武器'] if db[userId]['裝備']['副武器'] else '無'}\n")

    return embed


def createPlayerComponents(ctx: interactions.CommandContext, db: DataBase, nickname: str) -> List[interactions.SelectOption]:
    """Create 3 battle SelectOption 

    Args:
        ctx (interactions.CommandContext): Command Context
        db (DataBase): DataBase
        nickname (str): The nickname of the user

    Returns:
        List[interactions.SelectOption]: Returns a list of 3 battle SelectOption 
    """
    components: List[interactions.SelectOption] = [
        interactions.SelectOption(
            label="模擬對戰",
            value=f"{nickname}-模擬對戰",
            description="防禦措施做好坐滿的模擬對戰，致死機率極低，但得到的經驗也極低"
        ),
        interactions.SelectOption(
            label="實戰演練",
            value=f"{nickname}-實戰演練",
            description="阿就實戰演練阿你想要我說甚麼"
        ),
        interactions.SelectOption(
            label="西部對決",
            value=f"{nickname}-西部對決",
            description="來一場刺激的西部對決吧!在拿到大量經驗的同時，也很容易將對將對方擊殺"
        )
    ]

    return components


def reportToStr(line: Tuple[str, int], ind: int) -> str:
    """Transform a list[report, reportType] to embed content

    Args:
        line (Tuple[str, int]): (report, reportType)
            Report type:
                0: Normal attack
                1: Skill Attack
                2: Battle over(?)
        ind (int): The index of the report

    Returns:
        str: Discord embed content
    """

    # Discord code block prefix
    keyWord = "" if line[1] == 0 else ("fix" if line[1] == 1 else "diff")

    return f"```{keyWord}\n{'-' if line[1] == 2 else ''}{ind}: {line[0]}\n```"


def createReportEmbed(ctx: interactions.CommandContext, db: DataBase, reports: DataBase, reportId: str) -> interactions.Embed:
    """Create an embed for the report page

    Args:
        ctx (interactions.CommandContext): Command Context
        db (DataBase): DataBase
        reports (DataBase): Report DataBase
        reportId (str): The ID of the report

    Returns:
        interactions.Embed: Returns an embed for the report page
    """

    userId = str(ctx.user.id)

    # Get the current page
    pageNum = Storage(userId)["戰報頁數"]

    # Get the report
    report = reports[reportId]
    lines: str = report["戰報"]

    # Check if the pageNum has reached the limit
    if pageNum * linePerPage >= len(lines):
        pageNum = max(0, len(lines) / linePerPage - 1)

    # Page end
    end = (pageNum+1) * linePerPage
    end = end if end <= len(lines) else len(lines)

    # Get the discord embed content
    lines = [reportToStr(line, ind+1) for ind, line in enumerate(lines)]

    # Get the lines in the right area
    lines = lines[pageNum*linePerPage:end]

    # Create the embed
    embed = interactions.Embed(title=f"戰報-{reportId}", color=0xFFA500)
    embed.add_field(name="攻擊方", value=report["攻擊方"]["暱稱"])
    embed.add_field(name="防守方 ", value=report["防守方"]["暱稱"], inline=True)
    embed.add_field(name="類型", value=report["類型"])
    embed.add_field(name="戰報", value="".join(lines))

    return embed


def createReportComponents(ctx: interactions.CommandContext, db: DataBase, reports: DataBase, report: str) -> interactions.ActionRow:
    """Create an ActionRow with prev/next page button

    Args:
        ctx (interactions.CommandContext): Command Context
        db (DataBase): DataBase
        reports (DataBase): Report DataBase
        report (str): The ID of the report

    Returns:
        interactions.ActionRow: Return an ActionRow with prev/next page button
    """

    userId = str(ctx.user.id)
    pageNum = Storage(userId)["戰報頁數"]

    return interactions.ActionRow(
        components=[

            # Previous page
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY if Storage(
                    userId)["戰報頁數"] else interactions.ButtonStyle.DANGER,
                label="前一頁",
                custom_id="reportPrevPage",
                disabled=not pageNum
            ),

            # Next page
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY if (Storage(userId)[
                    "戰報頁數"]+1) * linePerPage < len(reports[report]["戰報"]) else interactions.ButtonStyle.DANGER,
                label="下一頁",
                custom_id="reportNextPage",
                disabled=(Storage(userId)[
                    "戰報頁數"]+1) * linePerPage >= len(reports[report]["戰報"])
            )
        ]
    )


def createPlayerReportEmbed(ctx: interactions.CommandContext, db: DataBase, reports: DataBase):
    """ ToDo """
    userId = str(ctx.user.id)
    atkList = db[userId]["戰報"]["攻擊"]
    defList = db[userId]["戰報"]["防守"]


class CombatUI(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client
        self.db: DataBase = db
        self.reports: DataBase = reports

    @interactions.extension_command(name="player", description="查詢其他玩家", options=[
        interactions.Option(
            name="nickname",
            description="該玩家的暱稱",
            type=interactions.OptionType.STRING,
            autocomplete=True,
            required=True
        )
    ])
    async def player(self, ctx: interactions.CommandContext, nickname: str):
        embed = await createPlayerEmbed(ctx, self.db, nickname)
        if validPlayer(self.db, nickname):
            await ctx.send(embeds=[embed], components=[
                interactions.ActionRow(
                    components=[

                        # Dropdown menu
                        interactions.SelectMenu(
                            custom_id="startFight",
                            options=createPlayerComponents(
                                ctx, self.db, nickname),
                            placeholder="來對戰吧"
                        )
                    ]
                )
            ])
        else:
            await ctx.send(embeds=[embed])

    @interactions.extension_autocomplete(command="player", name="nickname")
    async def auto_player_nick(self, ctx: interactions.CommandContext, user_input: str = ""):
        # Get all the player name
        nameList: List[str] = [player["暱稱"]
                               for player in db.getData()]

        PLAYER_NICK_COUNT = 20

        if user_input:
            final = [name
                     for name in nameList if len(name) >= len(user_input) and name.startswith(user_input)]
            sorted(final)

            await ctx.populate([interactions.Choice(
                name=name,
                value=name
            ) for name in final[:min(len(final), PLAYER_NICK_COUNT)]])
        else:
            nameList.sort()
            await ctx.populate([interactions.Choice(
                name=name,
                value=name
            ) for name in nameList[:min(len(nameList), PLAYER_NICK_COUNT)]])

    @interactions.extension_component("startFight")
    async def startFight(self, ctx: interactions.CommandContext, value: List[str]):
        """ Simulate a fight """

        userId = str(ctx.user.id)
        value = value[0].rsplit("-")

        enemyName = value[0]
        enemyInd = [item["暱稱"]
                    for item in self.db.getData()].index(enemyName)
        enemyId = self.db.getKeys()[enemyInd]

        fightType = value[1]

        # TODO: Implement die mechanic
        #dieChance = [0.001, 0.01, 0.2]
        dieChance: int = 0
        if fightType == "模擬切磋":
            dieChance = 0.001
        elif fightType == "實戰演練":
            dieChance = 0.01
        else:
            dieChance = 0.2

        # Create Character using the player's data
        user: Character = CharacterNames[self.db[userId]["角色"]]
        enemy: Character = CharacterNames[self.db[enemyId]["角色"]]

        # Get player's weapon
        userWeapons: List[Weapon] = []
        for slotName in armorName:
            if not self.db[userId]["裝備"][slotName]:
                continue

            # Get index
            ind = [item["名稱"] for item in self.db[userId]["背包"]
                   ["裝甲武器"]].index(self.db[userId]["裝備"][slotName])

            # Add weapon
            if self.db[userId]["背包"]["裝甲武器"][ind]["武器類型"]:
                userWeapons.append(
                    WeaponNames[self.db[userId]["背包"]["裝甲武器"][ind]["武器類型"]]())

        # Get enemy's weapon
        enemyWeapons: List[Weapon] = []
        for slotName in armorName:
            if not self.db[enemyId]["裝備"][slotName]:
                continue

            # Get index
            ind = [item["名稱"] for item in self.db[enemyId]["背包"]
                   ["裝甲武器"]].index(self.db[enemyId]["裝備"][slotName])

            # Add weapon
            if self.db[enemyId]["背包"]["裝甲武器"][ind]["武器類型"]:
                enemyWeapons.append(
                    WeaponNames[self.db[enemyId]["背包"]["裝甲武器"][ind]["武器類型"]]())

        # Get player's armor stats
        armorStats = {"血量": 0, "攻擊": 0, "防禦": 0}
        nameList = [item["名稱"] for item in self.db[userId]["背包"]["裝甲武器"]]

        for aName in armorName:
            name = self.db[userId]["裝備"][aName]
            if name and self.db[userId]["背包"]["裝甲武器"][nameList.index(name)]["裝備"]:
                ind = nameList.index(name)
                armorStats["血量"] += self.db[userId]["背包"]["裝甲武器"][ind]["數值"]["血量"]
                armorStats["攻擊"] += self.db[userId]["背包"]["裝甲武器"][ind]["數值"]["攻擊"]
                armorStats["防禦"] += self.db[userId]["背包"]["裝甲武器"][ind]["數值"]["防禦"]

        # Player's total stats
        UserHp = self.db[userId]['狀態']['血量'] + \
            armorStats['血量']+self.db[userId]['魔力量']['血量']
        UserAtk = self.db[userId]['狀態']['攻擊'] + \
            armorStats['攻擊']+self.db[userId]['魔力量']['攻擊']
        UserDef = self.db[userId]['狀態']['防禦'] + \
            armorStats['防禦']+self.db[userId]['魔力量']['防禦']
        UserStr = self.db[userId]['狀態']['體力']+self.db[userId]['魔力量']['體力']
        UserAgi = self.db[userId]['狀態']['敏捷']+self.db[userId]['魔力量']['敏捷']
        UserSkl = self.db[userId]['狀態']['技巧']+self.db[userId]['魔力量']['技巧']
        UserInt = self.db[userId]['狀態']['智力']+self.db[userId]['魔力量']['智力']
        userStats = {
            "血量": UserHp,
            "攻擊": UserAtk,
            "防禦": UserDef,
            "體力": UserStr,
            "技巧": UserSkl,
            "敏捷": UserAgi,
            "智力": UserInt
        }

        # Get enemy's armor stats
        armorStats = {"血量": 0, "攻擊": 0, "防禦": 0}
        nameList = [item["名稱"] for item in self.db[enemyId]["背包"]["裝甲武器"]]
        for aName in armorName:
            name = self.db[enemyId]["裝備"][aName]
            if name and self.db[enemyId]["背包"]["裝甲武器"][nameList.index(name)]["裝備"]:
                ind = nameList.index(name)
                armorStats["血量"] += self.db[enemyId]["背包"]["裝甲武器"][ind]["數值"]["血量"]
                armorStats["攻擊"] += self.db[enemyId]["背包"]["裝甲武器"][ind]["數值"]["攻擊"]
                armorStats["防禦"] += self.db[enemyId]["背包"]["裝甲武器"][ind]["數值"]["防禦"]

        # Get enemy's total stats
        EnemyHp = self.db[enemyId]['狀態']['血量'] + \
            armorStats['血量']+self.db[enemyId]['魔力量']['血量']
        EnemyAtk = self.db[enemyId]['狀態']['攻擊'] + \
            armorStats['攻擊']+self.db[enemyId]['魔力量']['攻擊']
        EnemyDef = self.db[enemyId]['狀態']['防禦'] + \
            armorStats['防禦']+self.db[enemyId]['魔力量']['防禦']
        EnemyStr = self.db[enemyId]['狀態']['體力']+self.db[enemyId]['魔力量']['體力']
        EnemyAgi = self.db[enemyId]['狀態']['敏捷']+self.db[enemyId]['魔力量']['敏捷']
        EnemySkl = self.db[enemyId]['狀態']['技巧']+self.db[enemyId]['魔力量']['技巧']
        EnemyInt = self.db[enemyId]['狀態']['智力']+self.db[enemyId]['魔力量']['智力']
        enemyStats = {
            "血量": EnemyHp,
            "攻擊": EnemyAtk,
            "防禦": EnemyDef,
            "體力": EnemyStr,
            "技巧": EnemySkl,
            "敏捷": EnemyAgi,
            "智力": EnemyInt
        }

        # Get report
        report = Duel(
            user(self.db[userId]['暱稱'],
                 userStats.copy(), userWeapons),
            enemy(self.db[enemyId]['暱稱'],
                  enemyStats.copy(), enemyWeapons)
        )

        # Write to database
        self.reports[str(self.reports["數量"])] = {
            "類型": fightType,
            "攻擊方": {
                "ID": userId,
                "暱稱": self.db[userId]["暱稱"],
                "角色": self.db[userId]["角色"],
                "等級": self.db[userId]["等級"],
                "狀態": userStats,
                "裝備": self.db[userId]["裝備"]
            },
            "防守方": {
                "ID": enemyId,
                "暱稱": self.db[enemyId]["暱稱"],
                "角色": self.db[enemyId]["角色"],
                "等級": self.db[enemyId]["等級"],
                "狀態": enemyStats,
                "裝備": self.db[enemyId]["裝備"]
            },
            "戰報": report
        }
        self.db[userId, "戰報", "攻擊"] = self.db[userId]["戰報"]["攻擊"] + \
            [str(self.reports["數量"]), ]
        self.db[enemyId, "戰報", "防守"] = self.db[enemyId]["戰報"]["防守"] + \
            [str(self.reports["數量"]), ]
        self.reports["數量"] = self.reports["數量"]+1

        await ctx.send(embeds=[createReportEmbed(ctx, self.db, self.reports, str(self.reports["數量"]-1))], components=[createReportComponents(ctx, self.db, self.reports, str(self.reports["數量"]-1))])

    @interactions.extension_component("reportPrevPage")
    async def reportPrevPage(self, ctx: interactions.CommandContext):
        userId = str(ctx.user.id)
        reportId = ctx.message.embeds[0].title.rsplit("-")[1]

        Storage(userId)["戰報頁數"] = Storage(userId)["戰報頁數"]-1

        components = createReportEmbed(
            ctx, self.db, self.reports, reportId)

        await ctx.edit(embeds=[components], components=[createReportComponents(ctx, self.db, self.reports, reportId)])

    @interactions.extension_component("reportNextPage")
    async def reportNextPage(self, ctx: interactions.CommandContext):
        userId = str(ctx.user.id)
        reportId = ctx.message.embeds[0].title.rsplit("-")[1]

        Storage(userId)["戰報頁數"] = Storage(userId)["戰報頁數"]+1

        components = createReportEmbed(
            ctx, self.db, self.reports, reportId)

        await ctx.edit(embeds=[components], components=[createReportComponents(ctx, self.db, self.reports, reportId)])

    @interactions.extension_command(name="report", description="查看戰報", options=[
        interactions.Option(
            name="reportid",
            description="戰報的編號",
            required=True,
            type=interactions.OptionType.STRING,
        )
    ])
    async def report(self, ctx: interactions.CommandContext, reportid: str):
        if not self.reports.contains((), reportid):
            await ctx.send("查無此戰報!")
        userId = str(ctx.user.id)
        Storage(userId)["戰報頁數"] = 0
        components = createReportEmbed(
            ctx, self.db, self.reports, reportid)
        await ctx.send(embeds=[components], components=[createReportComponents(ctx, self.db, self.reports, reportid)])


def setup(client):
    CombatUI(client)
