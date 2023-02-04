import interactions

bot = interactions.Client(
    token="MTAzMTU1ODc0MDMyOTEwMzM3MA.G-jqRL.Rtxd1qKiXQwCXEto0lBoGtPkXHQ8ug0SJYiaP0", logging=True)
bot.load("src.extensions.BasicUi")
bot.load("src.extensions.InventoryUI")
bot.load("src.extensions.CombatUI")

bot.start()
