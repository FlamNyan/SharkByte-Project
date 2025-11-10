class Character:
    def __init__(self, name, health, money, armor, damage):
        self.name = name
        self.health = health
        self.money = money
        self.armor = armor
        self.damage = damage
        # Simple inventory list for items bought in the shop
        self.inventory = []
        # Vigor resource used by combat (starts at 0 for player & enemies)
        self.vigor = 0


enemy_templates = [
    {
        "name": "Goblin Cutthroat",
        "health": 12,
        "armor": 3,
        "damage": 8,
        "gold_min": 14,
        "gold_max": 20,
        # Nimble and tricksy – likes feints
        "preferred_action": "feint",
        # 45% spawn chance
        "spawn_weight": 40,
    },
    {
        "name": "Skeleton Knight",  # your "Skeleton King"
        "health": 18,
        "armor": 6,
        "damage": 4,
        "gold_min": 18,
        "gold_max": 26,
        # Heavily armored – likes to block and punish
        "preferred_action": "block",
        # 35% spawn chance
        "spawn_weight": 35,
    },
    {
        "name": "Bandit Raider",
        "health": 16,
        "armor": 4,
        "damage": 6,
        "gold_min": 20,
        "gold_max": 30,
        # Aggressive brawler – likes to attack
        "preferred_action": "attack",
        # 20% spawn chance
        "spawn_weight": 25,
    },
]
