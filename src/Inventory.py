from typing import Dict, List


class Inventory:
    @staticmethod
    def AddItem(inventory: List[Dict], name: str, amount: int):
        items = [item["名稱"] for item in inventory]

        if name in items:
            # The item does exist
            ind = items.index(name)
            inventory[ind]["數量"] += amount
        else:
            # The item does not yet exist
            inventory.append({"名稱": name, "數量": amount})

        return inventory

    @staticmethod
    def Remove(inventory: List[Dict], name: str, amount: int):
        items = [item["名稱"] for item in inventory]

        ind = items.index(name)
        inventory[ind]["數量"] -= amount

        # Delete the item if the item count reaches 0 or less
        if inventory[ind]["數量"] <= 0:
            inventory.pop(ind)

        return inventory
