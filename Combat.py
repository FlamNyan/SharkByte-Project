
#Combat Class

class Combat:

    def totalDamage(self, item, MainCharacter):
    
        pass

    

          
    
    def TurnAction(self, playerAction, enemyAction, playerHealth, enemyHealth):

        if playerAction == "a" and enemyAction == "a":
            playerHealth = playerHealth
            enemyHealth = enemyHealth

        elif playerAction == "b" and enemyAction == "b":

            playerHealth = playerHealth
            enemyHealth = enemyHealth

        elif playerAction == "a" and enemyAction == "b":
            playerHealth == playerHealth
            enemyHealth -= 20

        elif playerAction == "b" and enemyAction == "a":
            playerHealth -= 20
            enemyHealth == enemyHealth
