
#Combat Class

class Combat:

    def totalDamage(self, item, Character):

        weapon = None

        for item in Character.inventory:
            if item.get("Type") == "weapon":
                weapon = item
                break
        
        if weapon:
            total_damage = getattr(Character, "damage", 0) + weapon.get("Damage", 0)
        else:
            total_damage = getattr(Character, "damage", 0)

        return total_damage
        
    

          
    
    def TurnAction(self, playerAction, enemyAction, playerHealth, enemyHealth, enemyItem, playerItem, player, enemy):

        """
        playerAction, enemyAction: 'a' = attack, 'b' = block
        player, enemy: objects with .health attribute
        playerItem, enemyItem: item dictionaries (weapons)
        """

        playerDamage = self.totalDamage(playerItem, player)
        enemyDamage = self.totalDamage(enemyItem, enemy) if enemyItem else 10

        if playerAction == "a" and enemyAction == "a":
            playerHealth = playerHealth
            enemyHealth = enemyHealth

        elif playerAction == "b" and enemyAction == "b":

            playerHealth = playerHealth
            enemyHealth = enemyHealth

        elif playerAction == "a" and enemyAction == "b":
            playerHealth == playerHealth
            enemyHealth -= playerDamage

        elif playerAction == "b" and enemyAction == "a":
            playerHealth -= enemyDamage
            enemyHealth == enemyHealth
