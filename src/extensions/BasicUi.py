import interactions


from src.Storage import Storage
from src.DataBase import DataBase
from src.Inventory import Inventory
from src.UI import UI
from src.Story import Story
from src.extensions.db import db

from typing import List

DefaultData = {
    "角色": "騎士",
    "等級": 1,
    "經驗值": 0,
    "狀態": {
        "血量": 500,
        "攻擊": 25,
        "防禦": 20,
        "體力": 25,
        "敏捷": 35,
        "智力": 25
    },
    "魔力量": {
        "血量": 0,
        "攻擊": 0,
        "防禦": 0,
        "體力": 0,
        "敏捷": 0,
        "智力": 0
    },
    "可分配魔力量": 0,
    "總魔力量": 0,
    "背包": {
        "裝甲武器": [],
        "物品": []
    },
    "裝備": {
        "頭盔": "",
        "胸甲": "",
        "腿甲": "",
        "鞋子": "",
        "主武器": "",
        "副武器": ""
    },
    "經濟": 0
}

statsName = ["血量", "攻擊", "防禦", "體力", "技巧", "敏捷", "智力"]
armorName = ["頭盔", "胸甲", "腿甲", "鞋子", "主武器", "副武器"]


class RPG(interactions.Extension):
    """This is the main class for the rpg game"""

    def __init__(self, client):
        self.client: interactions.Client = client
        self.db: DataBase = db

    @interactions.extension_command(name="register", description="Use this command to get started!（≧∇≦）")
    async def register(self, ctx: interactions.CommandContext):
        userId = str(ctx.user.id)
        if not self.db.contains((), userId):
            self.db[userId] = DefaultData
            await ctx.send("Successfully create your profile!")
        else:
            await ctx.send("You already have a profile!")

    @interactions.extension_command(name="profile", description="Use this command to show your profile!!")
    async def profile(self, ctx: interactions.CommandContext):
        userId = str(ctx.user.id)

        # Create the embed
        embed = interactions.Embed(
            title="玩家檔案",
            color=0xFFA500
        )
        embed.set_author(f"{ctx.user.username}-profile",
                         icon_url=ctx.user.avatar_url)
        embed.set_thumbnail(ctx.user.avatar_url)

        # Character
        embed.add_field(name="**角色**", value=self.db[userId]["角色"])

        # Level, exp, etc.
        embed.add_field(
            name="進度", value=f"**等級**: {self.db[userId]['等級']}\n**經驗**: {self.db[userId]['經驗值']}/{(self.db[userId]['等級']+1)*10+90}\n")

        # Get total armor stats
        armorStats = {"血量": 0, "攻擊": 0, "防禦": 0}
        nameList = [item["名稱"] for item in self.db[userId]["背包"]["裝甲武器"]]
        for aName in armorName:
            name = self.db[userId]["裝備"][aName]
            if name and self.db[userId]["背包"]["裝甲武器"][nameList.index(name)]["裝備"]:
                ind = nameList.index(name)
                armorStats["血量"] += self.db[userId]["背包"]["裝甲武器"][ind]["數值"]["血量"]
                armorStats["攻擊"] += self.db[userId]["背包"]["裝甲武器"][ind]["數值"]["攻擊"]
                armorStats["防禦"] += self.db[userId]["背包"]["裝甲武器"][ind]["數值"]["防禦"]

        # Get total stats
        Hp = self.db[userId]['狀態']['血量'] + \
            armorStats['血量']+self.db[userId]['魔力量']['血量']
        Atk = self.db[userId]['狀態']['攻擊'] + \
            armorStats['攻擊']+self.db[userId]['魔力量']['攻擊']
        Def = self.db[userId]['狀態']['防禦'] + \
            armorStats['防禦']+self.db[userId]['魔力量']['防禦']
        Str = self.db[userId]['狀態']['體力']+self.db[userId]['魔力量']['體力']
        Agi = self.db[userId]['狀態']['敏捷']+self.db[userId]['魔力量']['敏捷']
        Skl = self.db[userId]['狀態']['技巧']+self.db[userId]['魔力量']['技巧']
        Int = self.db[userId]['狀態']['智力']+self.db[userId]['魔力量']['智力']
        embed.add_field(name="數值", value=f"❤️ **血量**: {Hp}{'(裝備+'+str(armorStats['血量']) if armorStats['血量'] else ''}{', 魔力點+'+str(self.db[userId]['魔力量']['血量']) if self.db[userId]['魔力量']['血量'] else ''}\n"
                        f"🔪 **攻擊**: {Atk}{'(裝備+'+str(armorStats['攻擊']) if armorStats['攻擊'] else ''}{', 魔力點+'+str(self.db[userId]['魔力量']['攻擊']) if self.db[userId]['魔力量']['攻擊'] else ''}\n"
                        f"🛡️ **防禦**: {Def}{'(裝備+'+str(armorStats['防禦']) if armorStats['防禦'] else ''}{', 魔力點+'+str(self.db[userId]['魔力量']['防禦']) if self.db[userId]['魔力量']['防禦'] else ''}\n"
                        f"🏃 **體力**: {Str}{'(魔力點+'+str(self.db[userId]['魔力量']['體力']) if self.db[userId]['魔力量']['體力'] else ''}\n"
                        f"🛹 **敏捷**: {Agi}{'(魔力點+'+str(self.db[userId]['魔力量']['敏捷']) if self.db[userId]['魔力量']['敏捷'] else ''}\n"
                        f"🔧 **技巧**: {Skl}{'(魔力點+'+str(self.db[userId]['魔力量']['技巧']) if self.db[userId]['魔力量']['技巧'] else ''}\n"
                        f"🧠 **智力**: {Int}{'(魔力點+'+str(self.db[userId]['魔力量']['智力']) if self.db[userId]['魔力量']['智力'] else ''}\n")

        # Armor/Weapon
        embed.add_field(name="裝備", value=f"**頭盔**: {self.db[userId]['裝備']['頭盔'] if self.db[userId]['裝備']['頭盔'] else '無'}\n"
                        f"**胸甲**: {self.db[userId]['裝備']['胸甲'] if self.db[userId]['裝備']['胸甲'] else '無'}\n"
                        f"**腿甲**: {self.db[userId]['裝備']['腿甲'] if self.db[userId]['裝備']['腿甲'] else '無'}\n"
                        f"**鞋子**: {self.db[userId]['裝備']['鞋子'] if self.db[userId]['裝備']['鞋子'] else '無'}\n"
                        f"**主武器**: {self.db[userId]['裝備']['主武器'] if self.db[userId]['裝備']['主武器'] else '無'}\n"
                        f"**副武器**: {self.db[userId]['裝備']['副武器'] if self.db[userId]['裝備']['副武器'] else '無'}\n")

        embed.add_field(name="經濟", value=f"{self.db[userId]['經濟']}元")

        await ctx.send(embeds=[embed])

    @interactions.extension_command(name="skillpoint", description="Where you can manage your skillpoint")
    async def skillpoint(self, ctx: interactions.CommandContext):
        userId = str(ctx.user.id)

        if not Storage(userId)["魔力點剩餘"]:
            Storage(userId)["魔力點剩餘"] = self.db[userId]["可分配魔力量"]

        components = [
            interactions.ActionRow(
                components=[UI.createSkillMenuComponent()]
            )
        ]

        # Didn't use all the skillpoints
        if Storage(userId)["魔力點剩餘"]:
            components.append(interactions.ActionRow(
                components=[
                    interactions.Button(
                        style=interactions.ButtonStyle.DANGER,
                        label="送出",
                        custom_id="sendSkillPoint",
                        disabled=True
                    )
                ]
            )
            )
        else:
            components.append(interactions.ActionRow(
                components=[
                    interactions.Button(
                        style=interactions.ButtonStyle.DANGER,
                        label="送出",
                        custom_id="sendSkillPoint",
                        disabled=False
                    )
                ]
            ))

        await ctx.send(embeds=[UI.createSkillMenuEmbed(ctx, self.db)], components=components)

    @interactions.extension_component("skillmenu")
    async def skillmenu(self, ctx: interactions.CommandContext, value):
        userId = str(ctx.user.id)

        if not Storage(userId)["魔力點剩餘"]:
            Storage(userId)["魔力點剩餘"] = self.db[userId]["可分配魔力量"]

        embed = UI.createSkillDesEmbed(ctx, self.db, value[0])

        await ctx.edit(embeds=[embed], components=[
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label="+",
                custom_id="skillpoint_plus"
            ),
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label="-",
                custom_id="skillpoint_minus"
            ),
            interactions.Button(
                style=interactions.ButtonStyle.DANGER,
                label="返回",
                custom_id="skillpoint_back"
            )
        ])

    @interactions.extension_component("skillpoint_plus")
    async def skillpoint_plus(self, ctx: interactions.CommandContext):
        userId = str(ctx.user.id)

        if not Storage(userId)["魔力點剩餘"]:
            Storage(userId)["魔力點剩餘"] = self.db[userId]["可分配魔力量"]

        # Used all the skillpoints
        if not Storage(userId)["魔力點剩餘"]:
            embed = UI.createSkillDesEmbed(
                ctx, self.db, ctx.message.embeds[0].title)

            await ctx.edit(embeds=[embed], components=[
                interactions.Button(
                    style=interactions.ButtonStyle.PRIMARY,
                    label="+",
                    custom_id="skillpoint_plus"
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.PRIMARY,
                    label="-",
                    custom_id="skillpoint_minus"
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.DANGER,
                    label="返回",
                    custom_id="skillpoint_back"
                )
            ])

            await ctx.send("魔力點不夠了!!", ephemeral=True)

            return

        Storage(userId)["魔力點分配", ctx.message.embeds[0].title] = (Storage(
            userId)["魔力點分配"][ctx.message.embeds[0].title]+1)
        Storage(userId)["魔力點剩餘"] = (Storage(userId)["魔力點剩餘"]-1)

        embed = UI.createSkillDesEmbed(
            ctx, self.db, ctx.message.embeds[0].title)

        await ctx.edit(embeds=[embed], components=[
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label="+",
                custom_id="skillpoint_plus"
            ),
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label="-",
                custom_id="skillpoint_minus"
            ),
            interactions.Button(
                style=interactions.ButtonStyle.DANGER,
                label="返回",
                custom_id="skillpoint_back"
            )
        ])

    @interactions.extension_component("skillpoint_minus")
    async def skillpoint_minus(self, ctx: interactions.CommandContext):
        userId = str(ctx.user.id)

        if not Storage(userId)["魔力點剩餘"]:
            Storage(userId)["魔力點剩餘"] = self.db[userId]["可分配魔力量"]

        if not Storage(userId)["魔力點分配"][ctx.message.embeds[0].title]:
            embed = UI.createSkillDesEmbed(
                ctx, self.db, ctx.message.embeds[0].title)

            await ctx.edit(embeds=[embed], components=[
                interactions.Button(
                    style=interactions.ButtonStyle.PRIMARY,
                    label="+",
                    custom_id="skillpoint_plus"
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.PRIMARY,
                    label="-",
                    custom_id="skillpoint_minus"
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.DANGER,
                    label="返回",
                    custom_id="skillpoint_back"
                )
            ])

            await ctx.send("已經沒有魔力點了!!", ephemeral=True)
            return

        Storage(userId)["魔力點分配", ctx.message.embeds[0].title] = (Storage(
            userId)["魔力點分配"][ctx.message.embeds[0].title]-1)
        Storage(userId)["魔力點剩餘"] = (Storage(userId)["魔力點剩餘"]+1)

        embed = UI.createSkillDesEmbed(
            ctx, self.db, ctx.message.embeds[0].title)

        await ctx.edit(embeds=[embed], components=[
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label="+",
                custom_id="skillpoint_plus"
            ),
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label="-",
                custom_id="skillpoint_minus"
            ),
            interactions.Button(
                style=interactions.ButtonStyle.DANGER,
                label="返回",
                custom_id="skillpoint_back"
            )
        ])

    @interactions.extension_component("skillpoint_back")
    async def skillpoint_back(self, ctx: interactions.CommandContext):
        userId = str(ctx.user.id)

        components = [
            interactions.ActionRow(
                components=[UI.createSkillMenuComponent()]
            )
        ]

        if Storage(userId)["魔力點剩餘"]:
            components.append(interactions.ActionRow(
                components=[
                    interactions.Button(
                        style=interactions.ButtonStyle.DANGER,
                        label="送出",
                        custom_id="sendSkillPoint",
                        disabled=True
                    )
                ]
            ))
        else:
            components.append(interactions.ActionRow(
                components=[
                    interactions.Button(
                        style=interactions.ButtonStyle.DANGER,
                        label="送出",
                        custom_id="sendSkillPoint",
                        disabled=False
                    )
                ]
            ))

        await ctx.edit(embeds=[UI.createSkillMenuEmbed(ctx, self.db)], components=components)

    @interactions.extension_component("sendSkillPoint")
    async def sendSkillPoint(self, ctx: interactions.CommandContext):
        userId = str(ctx.user.id)

        # Set the skillpoints
        for name in statsName:
            self.db[userId, "魔力量", name] = self.db[userId]["魔力量"][name] + \
                Storage(userId)["魔力點分配"][name]

        # Reset the Storage data
        self.db[userId, "可分配魔力量"] = 0
        for name in statsName:
            Storage(userId)["魔力點分配", name] = 0

        await ctx.send("成功送出你的魔力點分配!", ephemeral=True)

    @interactions.extension_command(
        name="add_skillpoint",
        description="Add distributable skillpoint to your profile JUST FOR TESTING PURPOSES",
        options=[
            interactions.Option(
                name="amount",
                description="The amount of skillpoint you want to add",
                type=interactions.OptionType.INTEGER,
                require=True
            )
        ]
    )
    async def add_skillpoint(self, ctx: interactions.CommandContext, amount: int):
        userId = str(ctx.user.id)
        self.db[userId, "可分配魔力量"] = self.db[userId]["可分配魔力量"] + amount
        if not Storage(userId).contains((), "魔力點剩餘"):
            Storage(userId)["魔力點剩餘"] = self.db[userId]["可分配魔力量"]
        Storage(userId)["魔力點剩餘"] = Storage(userId)["魔力點剩餘"]+amount
        await ctx.send(f"成功新增{amount}可分配魔力量!!")

    @interactions.extension_command(name="story", description="Start a story!")
    async def story(self, ctx: interactions.CommandContext):
        """What the cinnamon toast fuck is this"""
        userId = str(ctx.user.id)
        if not Storage(userId).contains((), "story"):
            Storage(userId)["story"] = Story("story.json")
        if not Storage(userId).contains((), "storyId"):
            Storage(userId)["storyId"] = Storage(userId)["story"].initial
        embed = interactions.Embed(title="Story", description="Story")
        embed.set_author(name=ctx.user.username, url=ctx.user.avatar_url)
        embed.add_field(name="**內容**", value=Storage(userId)
                        ["story"].contents[Storage(userId)["storyId"]]["content"])
        await ctx.send(embeds=[embed], components=[
            interactions.SelectMenu(
                options=UI.createStoryComponents(ctx),
                custom_id="storyPick",
                placeholder="選擇你的選項!"
            )
        ])

    @interactions.extension_component("storyPick")
    async def storyPick(self, ctx: interactions.CommandContext, value: List):
        userId = str(ctx.user.id)
        Storage(userId)["storyId"] = value[0]
        embed = interactions.Embed(title="Story", description="Story")
        embed.set_author(name=ctx.user.username, url=ctx.user.avatar_url)
        embed.add_field(name="**內容**", value=Storage(userId)
                        ["story"].contents[value[0]]["content"])
        components = UI.createStoryComponents(ctx)
        if len(components):
            await ctx.send(embeds=[embed], components=[
                interactions.SelectMenu(
                    options=components,
                    custom_id="storyPick",
                    placeholder="選擇你的選項!"
                )
            ])
        else:
            await ctx.send(embeds=[embed])


def setup(client):
    RPG(client)
