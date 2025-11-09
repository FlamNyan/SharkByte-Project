class Character:
    def __init__(self, name, health, money, armor, damage):
        self.name = name
        self.health = health
        self.money = money
        self.armor = armor
        self.damage = damage
        # Simple inventory list for items bought in the shop
        self.inventory = []
        # Vigor resource used by combat (starts at 0)
        self.vigor = 0


enemy_templates = [
    {
        "name": "Goblin Cutthroat",
        "health": 12,
        "armor": 3,
        "damage": 4,
        "gold_min": 10,
        "gold_max": 20,
        # Nimble and tricksy – likes feints
        "preferred_action": "feint",
    },
    {
        "name": "Skeleton Knight",
        "health": 18,
        "armor": 5,
        "damage": 5,
        "gold_min": 15,
        "gold_max": 30,
        # Heavily armored – likes to block and punish
        "preferred_action": "block",
    },
    {
        "name": "Bandit Raider",
        "health": 16,
        "armor": 4,
        "damage": 6,
        "gold_min": 20,
        "gold_max": 40,
        # Aggressive brawler – likes to attack
        "preferred_action": "attack",
    },
]
