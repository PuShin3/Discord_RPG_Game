from __future__ import annotations
import interactions


from src.Storage import Storage
from src.DataBase import DataBase
from src.Inventory import Inventory
from src.UI import UI
from src.Story import Story

from src.extensions.db import db

from typing import List, Dict, Tuple
from functools import cmp_to_key

ObjectPerPage = 10

statsName = ["血量", "攻擊", "防禦", "體力", "敏捷", "智力"]
armorName = ["頭盔", "胸甲", "腿甲", "鞋子", "主武器", "副武器"]


def sortByEquipAndName(x: Dict, y: Dict) -> int:
    """ Sort function based on equipped and name """
    if x["裝備"]:
        return -1
    if y["裝備"]:
        return 1
    if x["名稱"] < y["名稱"]:
        return 1
    elif x["名稱"] > y["名稱"]:
        return -1
    else:
        return 0


def createPickInventoryEmbed(ctx: interactions.CommandContext, db: DataBase, name: str, categ: str) -> interactions.Embed:
    """Create an embed that contains the description of the item

    Args:
        ctx (interactions.CommandContext): Command Context
        db (DataBase): Database
        name (str): The name of the item
        categ (str): The category of the inventory

    Returns:
        interactions.Embed: The embed contained the description of the item.
    """

    userId = str(ctx.user.id)

    # Create the embed
    embed = interactions.Embed(
        title=name, color=0x13DD66)
    embed.set_author(f"查看{categ}背包裡的項目",
                     icon_url=ctx.user.avatar_url)

    # All of the item names in the inventory of that category
    items = [item["名稱"] for item in db[userId]["背包"][categ]]

    # The index of the item we're looking for
    item = db[userId]["背包"][categ][items.index(name)]

    embed.add_field(
        name="物品數量", value=item["數量"])

    if categ == "裝甲武器":
        # Weapon stats
        embed.add_field(name="數值", value=f"❤️ 血量: {item['數值']['血量']}\n"
                        f"🔪 攻擊: {item['數值']['攻擊']}\n"
                        f"🛡️ 防禦: {item['數值']['防禦']}\n"
                        f"🏋 重量: {item['數值']['重量']}\n")
    embed.add_field(name="描述", value=item["描述"])

    return embed


def createInventoryEmbed(ctx: interactions.CommandContext, db: DataBase, categ: str) -> Tuple:
    """Create a tuple that contains a menu embed and a list of options

    Args:
        ctx (interactions.CommandContext): Command Context
        db (DataBase): DataBase
        categ (str): The category of the inventory

    Returns:
        Tuple: Returns a tuple with a length of 2 that contains
            0: The item menu embed.
            1: The options that contains all the item in the menu.
    """
    userId = str(ctx.user.id)\

    # Create the embed
    embed = interactions.Embed(title="玩家背包", color=0xFF0000)
    embed.set_author(f"{ctx.user.username}-{categ}背包",
                     icon_url=ctx.user.avatar_url)

    options = []
    items = ""
    count = ""

    # Check if the start of the page has gone beyond the length of the inventory
    if Storage(userId)["背包頁數"] * ObjectPerPage >= len(db[userId]["背包"][categ]):
        Storage(userId)["背包頁數"] = max(0, len(
            db[userId]["背包"][categ]) / ObjectPerPage - 1)

    end = (Storage(userId)["背包頁數"]+1) * ObjectPerPage
    # Check if the end of the page has gone beyond the length of the inventory
    end = end if end <= len(db[userId]["背包"][categ]) else len(
        db[userId]["背包"][categ])

    # Get the items in the range
    item = db[userId]["背包"][categ][Storage(userId)["背包頁數"] * ObjectPerPage:end]
    item = sorted(item, key=cmp_to_key(sortByEquipAndName)
                  if categ == "裝甲武器" else lambda x: x["名稱"])

    for i in item:
        items += f"{i['名稱']}\n"
        count += f"{i['數量']}\n"
        options.append(interactions.SelectOption(
            label=i['名稱'],
            value=f"{i['名稱']} {categ}",
            description=i['數量']
        ))

    # Add some random things if there's nothing
    if not options:
        options.append(interactions.SelectOption(
            label="這裡面沒東西qqq",
            value="無",
            description="你好窮",
            default=True
        ))
        embed.add_field(name="物品名稱", value="這邊沒東西，你真的好窮qqq")
    else:
        embed.add_field(name="物品名稱", value=items, inline=True)
        embed.add_field(name="數量", value=count, inline=True)

    return (embed, options, )


def createInventoryPageComponents(ctx: interactions.CommandContext, db: DataBase, categ: str) -> interactions.ActionRow:
    """Create a ActionRow that contains the PreviousPage and the NextPage button

    Args:
        ctx (interactions.CommandContext): Command Context
        db (DataBase): DataBase
        categ (str): The category of the inventory

    Returns:
        interactions.ActionRow: Returns a ActionRow that contains the PreviousPage and the NextPage button
    """
    userId = str(ctx.user.id)

    return interactions.ActionRow(
        components=[
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY if Storage(
                    userId)["背包頁數"] else interactions.ButtonStyle.DANGER,
                label="前一頁",
                custom_id="invenPrevPage",
                disabled=not Storage(userId)["背包頁數"]
            ),
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY if (Storage(userId)[
                    "背包頁數"]+1) * ObjectPerPage < len(db[userId]["背包"][categ]) else interactions.ButtonStyle.DANGER,
                label="下一頁",
                custom_id="invenNextPage",
                disabled=(Storage(userId)[
                    "背包頁數"]+1) * ObjectPerPage >= len(db[userId]["背包"][categ])
            )
        ]
    )


def createInvenPickComponents(ctx: interactions.CommandContext, db: DataBase, name: str, categ: str) -> List:
    """Create a list of components that contains 
        1.Equip/Unequip button if the item is a weapon/armor 

        2.A return button to the inventory menu


    Args:
        ctx (interactions.CommandContext): Command Context 
        db (DataBase): DataBase
        name (str): The name of the item
        categ (str): The category of the inventory

    Returns:
        List: Returns a list of components
    """

    # Return button
    components: List = [interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="返回",
        custom_id="inventory_back"
    ), ]

    userId = str(ctx.user.id)

    if categ == "裝甲武器":
        ind = [item["名稱"] for item in db[userId]["背包"][categ]].index(name)

        # Equip/Unequip button
        components.append(interactions.Button(
            style=interactions.ButtonStyle.DANGER if db[userId]["背包"][
                categ][ind]["裝備"] else interactions.ButtonStyle.PRIMARY,
            label="卸下" if db[userId]["背包"][categ][ind]["裝備"] else "裝備",
            custom_id="invenRemoveArmor" if db[userId]["背包"][categ][ind]["裝備"] else "invenEquipArmor"
        ))

    return components


def createArmorPickComponents(ctx: interactions.CommandContext, db: DataBase, name: str, categ: str) -> List:
    """Create a list of components that contains 
        1.Equip/Unequip button if the item is a weapon/armor 

        2.A return button to the armor menu


    Args:
        ctx (interactions.CommandContext): Command Context 
        db (DataBase): DataBase
        name (str): The name of the item
        categ (str): The category of the inventory

    Returns:
        List: Returns a list of components
    """

    # Return button
    components: List = [interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="返回",
        custom_id="armor_back"
    ), ]

    userId = str(ctx.user.id)

    ind = [item["名稱"] for item in db[userId]["背包"][categ]].index(name)

    # Equip/Unequip button
    components.append(interactions.Button(
        style=interactions.ButtonStyle.DANGER if db[userId]["背包"][
            categ][ind]["裝備"] else interactions.ButtonStyle.PRIMARY,
        label="卸下" if db[userId]["背包"][categ][ind]["裝備"] else "裝備",
        custom_id="invenRemoveArmor" if db[userId]["背包"][categ][ind]["裝備"] else "invenEquipArmor"
    ))

    return components


def createArmorEmbed(ctx: interactions.CommandContext, db: DataBase) -> interactions.Embed:
    """Create an embed that contains the armor menu

    Args:
        ctx (interactions.CommandContext): Command Context
        db (DataBase): DataBase

    Returns:
        interactions.Embed: Returns an embed that contains the armor menu
    """

    userId = str(ctx.user.id)

    # Create the embed
    embed: interactions.Embed = interactions.Embed(
        title="裝甲武器", color=0xFF0000)
    embed.set_author(f"{ctx.user.username}-裝甲武器",
                     icon_url=ctx.user.avatar_url)

    # Add the "WeaponType: Corresponding armor the character is wearing" field
    for aName in armorName:
        name = db[userId]["裝備"][aName]
        embed.add_field(name=f"**{aName}**",
                        value=f"    {name if name else '無'}")

    return embed


def createArmorComponents(ctx: interactions.CommandContext, db: DataBase) -> List[interactions.SelectOption]:
    """Create a list of SelectOptions that can be redirect to the chosen armor's page

    Args:
        ctx (interactions.CommandContext): Command Context
        db (DataBase): DataBase

    Returns:
        List[interactions.SelectOption]: Returns a list of SelectOptions
    """

    userId = str(ctx.user.id)
    options: List[interactions.SelectOption] = []

    for aName in armorName:
        name = db[userId]["裝備"][aName]
        # The value of the SelectOption is "armorType-armorName"
        # We can then get the chosen armorName by using split
        options.append(interactions.SelectOption(
            label=f"{aName}-{name if name else '無'}",
            value=f"{aName}-{name if name else '無'}",
            description=aName
        ))

    return options


class InventoryUI(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client
        self.db: DataBase = db

    @ interactions.extension_command(name="inventory", description="查看背包內的物品")
    async def inventory(self, ctx: interactions.CommandContext):
        ''' Just as the name suggested, calls the inventory menu '''

        userId = str(ctx.user.id)

        # Reset some temporary variables
        Storage(userId)["背包頁數"] = 0
        Storage(userId)["背包類型"] = "裝甲武器"

        # Create the embed
        components = createInventoryEmbed(
            ctx, self.db, Storage(userId)["背包類型"])

        # Send the embed and components
        await ctx.send(embeds=[components[0]], components=[
            # Dropdown menu
            interactions.ActionRow(
                components=[
                    interactions.SelectMenu(
                        options=components[1],
                        placeholder="你的物品",
                        custom_id="Pick inventory"
                    )
                ]
            ),

            # Create the buttons
            createInventoryPageComponents(
                ctx, self.db, Storage(userId)["背包類型"]),

            # Button for changing the category
            interactions.ActionRow(
                components=[
                    interactions.Button(
                        style=interactions.ButtonStyle.PRIMARY,
                        label=["裝甲武器", "物品"][Storage(
                            userId)["背包類型"] == "裝甲武器"],
                        custom_id="changeInvenCateg"
                    )
                ]
            )
        ])

    @interactions.extension_component("changeInvenCateg")
    async def changeInvenCateg(self, ctx: interactions.CommandContext):
        ''' Change the category of the inventory menu '''

        userId = str(ctx.user.id)

        # Reset some variables
        Storage(userId)["背包頁數"] = 0

        # Change the category
        Storage(userId)["背包類型"] = [
            "裝甲武器", "物品"][Storage(userId)["背包類型"] == "裝甲武器"]

        components = createInventoryEmbed(
            ctx, self.db, Storage(userId)["背包類型"])

        # EDIT the message
        await ctx.edit(embeds=[components[0]], components=[
            # Dropdown menu
            interactions.ActionRow(
                components=[
                    interactions.SelectMenu(
                        options=components[1],
                        placeholder="你的物品",
                        custom_id="Pick inventory"
                    )
                ]
            ),

            # Create the buttons
            createInventoryPageComponents(
                ctx, self.db, Storage(userId)["背包類型"]),

            # Button for changing the category
            interactions.ActionRow(
                components=[
                    interactions.Button(
                        style=interactions.ButtonStyle.PRIMARY,
                        label=["裝甲武器", "物品"][Storage(
                            userId)["背包類型"] == "裝甲武器"],
                        custom_id="changeInvenCateg"
                    )
                ]
            )
        ])

    @interactions.extension_component("invenPrevPage")
    async def invenPrevPage(self, ctx: interactions.CommandContext):
        userId = str(ctx.user.id)

        # Minus the page by 1
        Storage(userId)["背包頁數"] = max(0, Storage(userId)["背包頁數"]-1)

        components = createInventoryEmbed(
            ctx, self.db, Storage(userId)["背包類型"])

        # EDIT the message
        await ctx.edit(embeds=[components[0]], components=[
            # Dropdown menu
            interactions.ActionRow(
                components=[
                    interactions.SelectMenu(
                        options=components[1],
                        placeholder="你的物品",
                        custom_id="Pick inventory"
                    )
                ]
            ),

            # Create the buttons
            createInventoryPageComponents(
                ctx, self.db, Storage(userId)["背包類型"]),

            # Button for changing the category
            interactions.ActionRow(
                components=[
                    interactions.Button(
                        style=interactions.ButtonStyle.PRIMARY,
                        label=["裝甲武器", "物品"][Storage(
                            userId)["背包類型"] == "裝甲武器"],
                        custom_id="changeInvenCateg"
                    )
                ]
            )
        ])

    @interactions.extension_component("invenNextPage")
    async def invenNextPage(self, ctx: interactions.CommandContext):
        userId = str(ctx.user.id)

        # Add the page by 1
        Storage(userId)["背包頁數"] = Storage(userId)["背包頁數"]+1

        components = createInventoryEmbed(
            ctx, self.db, Storage(userId)["背包類型"])

        # EDIT the message
        await ctx.edit(embeds=[components[0]], components=[
            # Dropdown menu
            interactions.ActionRow(
                components=[
                    interactions.SelectMenu(
                        options=components[1],
                        placeholder="你的物品",
                        custom_id="Pick inventory"
                    )
                ]
            ),

            # Create the buttons
            createInventoryPageComponents(
                ctx, self.db, Storage(userId)["背包類型"]),

            # Button for changing the category
            interactions.ActionRow(
                components=[
                    interactions.Button(
                        style=interactions.ButtonStyle.PRIMARY,
                        label=["裝甲武器", "物品"][Storage(
                            userId)["背包類型"] == "裝甲武器"],
                        custom_id="changeInvenCateg"
                    )
                ]
            )
        ])

    @ interactions.extension_component("Pick inventory")
    async def pickInventory(self, ctx: interactions.CommandContext, value: List[str]):
        ''' The reaction after clicking the option in the dropdown menu in the inventory '''

        # Get the name and the category of the item
        valueSplitted = value[0].split(" ")
        name = valueSplitted[0]
        categ = valueSplitted[1]

        if (name == "無"):
            return

        embed = createPickInventoryEmbed(ctx, self.db, name, categ)
        components: List = createInvenPickComponents(ctx, self.db, name, categ)

        await ctx.send(embeds=[embed], components=[
            interactions.ActionRow(
                components=components
            )
        ])

    @interactions.extension_component("invenEquipArmor")
    async def invenEquipArmor(self, ctx: interactions.CommandContext):
        ''' Equip armor '''

        userId: str = str(ctx.user.id)
        name: str = ctx.message.embeds[0].title

        # All the names in the inventory
        nameList = [item["名稱"] for item in db[userId]["背包"]["裝甲武器"]]
        ind: int = nameList.index(name)

        armorType: str = self.db[userId]["背包"]["裝甲武器"][ind]["類型"]
        origName: str = self.db[userId]["裝備"][armorType]

        # If there's already an equipped weapon/armor
        if origName:
            origInd: int = nameList.index(origName)
            self.db[userId, "背包", "裝甲武器", origInd, "裝備"] = False

        # Equip the weapon/armor
        self.db[userId, "裝備", armorType] = name
        self.db[userId, "背包", "裝甲武器", ind, "裝備"] = True

        embed = createPickInventoryEmbed(ctx, self.db, name, "裝甲武器")
        components: List = createInvenPickComponents(
            ctx, self.db, name, "裝甲武器")

        await ctx.edit(embeds=[embed], components=[
            interactions.ActionRow(
                components=components
            )
        ])

        if origName and name != origName:
            # If there's already an equipped weapon/armor
            await ctx.send(f"將{armorType}上的{origName}替換成了{name}")
        else:
            await ctx.send(f"將{name}裝備到了{armorType}上")

    @interactions.extension_component("invenRemoveArmor")
    async def invenRemoveArmor(self, ctx: interactions.CommandContext):
        ''' Remove armor '''

        userId: str = str(ctx.user.id)
        name: str = ctx.message.embeds[0].title
        ind: int = [item["名稱"]
                    for item in self.db[userId]["背包"]["裝甲武器"]].index(name)
        armorType: str = self.db[userId]["背包"]["裝甲武器"][ind]["類型"]

        # Remove the weapon/armor
        self.db[userId, "裝備", armorType] = ""
        self.db[userId, "背包", "裝甲武器", ind, "裝備"] = False

        embed = createPickInventoryEmbed(ctx, self.db, name, "裝甲武器")
        components: List = createInvenPickComponents(
            ctx, self.db, name, "裝甲武器")

        await ctx.edit(embeds=[embed], components=[
            interactions.ActionRow(
                components=components
            )
        ])
        await ctx.send(f"將{armorType}上的{name}卸下來了")

    @ interactions.extension_component("sale")
    async def saleObject(self, ctx: interactions.CommandContext):
        userId = str(ctx.user.id)
        title = ctx.message.embeds[0].title
        money = hash(title) % 1000
        self.db[userId, "背包"] = Inventory.Remove(
            self.db[userId]["背包"], title, 1)
        self.db[userId, "經濟"] = self.db[userId]["經濟"] + money
        items = [item["名稱"] for item in self.db[userId]["背包"]]
        if ctx.message.embeds[0].title not in items:
            components = createInventoryEmbed(ctx, self.db, "裝甲武器")
            await ctx.edit(embeds=[components[0]], components=[
                interactions.ActionRow(
                    components=[
                        interactions.SelectMenu(
                            options=components[1],
                            placeholder="你的物品",
                            custom_id="Pick inventory"
                        )
                    ]
                ),
                createInventoryPageComponents(
                    ctx, self.db, Storage(userId)["背包類型"])
            ])
        else:
            await ctx.edit(embeds=[createPickInventoryEmbed(ctx, self.db, ctx.message.embeds[0].title, "裝甲武器")])
        await ctx.send(f"你賺到了{money}元!!", ephemeral=True)

    @ interactions.extension_component("inventory_back")
    async def inventory_back(self, ctx: interactions.CommandContext):
        userId = str(ctx.user.id)
        components = createInventoryEmbed(
            ctx, self.db, Storage(userId)["背包類型"])

        # EDIT the message
        await ctx.edit(embeds=[components[0]], components=[
            # Dropdown menu
            interactions.ActionRow(
                components=[
                    interactions.SelectMenu(
                        options=components[1],
                        placeholder="你的物品",
                        custom_id="Pick inventory"
                    )
                ]
            ),

            # Create the buttons
            createInventoryPageComponents(
                ctx, self.db, Storage(userId)["背包類型"]),

            # Button for changing the category
            interactions.ActionRow(
                components=[
                    interactions.Button(
                        style=interactions.ButtonStyle.PRIMARY,
                        label=["裝甲武器", "物品"][Storage(
                            userId)["背包類型"] == "裝甲武器"],
                        custom_id="changeInvenCateg"
                    )
                ]
            )
        ])

    @ interactions.extension_command(
        name="add_item",
        description="Add item to inventory JUST FOR TESTING PURPOSES",
        options=[
            interactions.Option(
                name="item_type",
                description="物品的種類",
                type=interactions.OptionType.STRING,
                require=True,
                choices=[
                    interactions.Choice(
                        name="armor",
                        value="裝甲武器"
                    ),
                    interactions.Choice(
                        name="item",
                        value="物品"
                    )
                ]
            ),
            interactions.Option(
                name="name",
                description="物品名稱",
                type=interactions.OptionType.STRING,
                require=True
            ),
            interactions.Option(
                name="count",
                description="數量",
                type=interactions.OptionType.INTEGER,
                require=True
            )
        ])
    async def addItem(self, ctx: interactions.CommandContext, item_type: str, name: str, count: int):
        userId = str(ctx.user.id)
        self.db[userId, "背包", item_type] = Inventory.AddItem(
            self.db[userId]["背包"][item_type], name, count)
        await ctx.send("成功")

    @interactions.extension_command(name="equipments", description="查看你目前的裝甲和武器")
    async def equipments(self, ctx: interactions.CommandContext):
        components = createArmorComponents(ctx, self.db)
        embed = createArmorEmbed(ctx, self.db)

        await ctx.send(embeds=[embed], components=[
            interactions.ActionRow(
                components=[
                    interactions.SelectMenu(
                        options=components,
                        placeholder="你的裝備",
                        custom_id="armorPick"
                    )
                ]
            )
        ])

    @interactions.extension_component("armorPick")
    async def armorPick(self, ctx: interactions.CommandContext, value: List[str]):
        userId = str(ctx.user.id)

        # Get the name of the item
        name = value[0].split("-")[-1]
        if (name == "無"):
            return

        embed = createPickInventoryEmbed(ctx, self.db, name, "裝甲武器")
        components: List = createArmorPickComponents(
            ctx, self.db, name, "裝甲武器")

        await ctx.edit(embeds=[embed], components=[
            interactions.ActionRow(
                components=components
            )
        ])

    @interactions.extension_component("armor_back")
    async def armor_back(self, ctx: interactions.COmmandContext):
        components = createArmorComponents(ctx, self.db)
        embed = createArmorEmbed(ctx, self.db)

        await ctx.send(embeds=[embed], components=[
            interactions.ActionRow(
                components=[
                    interactions.SelectMenu(
                        options=components,
                        placeholder="你的裝備",
                        custom_id="armorPick"
                    )
                ]
            )
        ])


def setup(client):
    InventoryUI(client)
