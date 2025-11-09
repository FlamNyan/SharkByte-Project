import time
import random
from UI import slow_print

class Combat:
    def apply_armor_damage(self, character, dmg):
        """Damage goes to armor first, then spills into health."""
        if dmg <= 0:
            return
        if character.armor > 0:
            character.armor -= dmg
            if character.armor < 0:
                overflow = -character.armor
                character.armor = 0
                character.health -= overflow
        else:
            character.health -= dmg

    def apply_hp_damage(self, character, dmg):
        if dmg <= 0:
            return
        character.health -= dmg

    def resolve_turn(self, player, enemy, player_action, enemy_action):
        """
        Apply combat rules and return a list of message strings
        explaining what happened this turn.

        Base rules:

        - If both Attack, no damage, both +1 Vigor.
        - If one Attacks and one Blocks:
            - Blocker takes half damage to armor (or HP if no armor).
            - Blocker gains +1 Vigor.
        - If one Attacks and one Feints:
            - Feinter takes critical damage.
        - If both Block, no damage, both +1 Vigor.
        - If one Blocks and one Feints:
            - Blocker takes full damage to armor.
        - If both Feint, both take minimal damage, no stat changes.

        Specials (player only for now):

        - heavy_attack:
            - Treated as an Attack.
            - Uses base damage * 2 when it actually lands.
            - If it hits a Block, the enemy's guard always breaks:
              * Their armor is set to 0.
              * If your base damage would overflow past their armor,
                the overflow is doubled and applied to HP.

        - fortify:
            - Treated as a Block.
            - This turn, any armor damage the player would take from blocking
              is reduced to 0 (no armor lost).
        """
        messages = []

        p = player
        e = enemy

        # Flags for player specials
        p_heavy = (player_action == "heavy_attack")
        p_fortify = (player_action == "fortify")

        # Reserved for future enemy specials
        e_heavy = False
        e_fortify = False

        # Effective actions for the rule table
        def effective_action(action, is_heavy, is_fortify):
            if is_heavy:
                return "attack"
            if is_fortify:
                return "block"
            return action

        pa = effective_action(player_action, p_heavy, p_fortify)
        ea = effective_action(enemy_action, e_heavy, e_fortify)

        # Base damage values (not yet doubled)
        base_p_dmg = p.damage
        base_e_dmg = e.damage

        # Helper lines
        def line_player_gain_vigor():
            return f"{p.name} steels their resolve. (+1 Vigor)"

        def line_enemy_gain_vigor():
            return f"{e.name} looks more focused. (+1 Vigor)"

        # --- Attack vs Attack ---
        if pa == "attack" and ea == "attack":
            messages.append("Steel clashes against steel as both sides lunge in!")
            messages.append("No clean hit is landed, but tension rises.")
            p.vigor += 1
            e.vigor += 1
            messages.append(line_player_gain_vigor())
            messages.append(line_enemy_gain_vigor())
            return messages

        # --- Attack vs Block / Block vs Attack ---
        # Remember: Fortify -> block but no armor loss for that character.
        if pa == "attack" and ea == "block":
            # Enemy is the blocker
            # Heavy Attack: always break guard, overflow (if any) is doubled to HP.
            if p_heavy and not e_fortify:
                prev_armor = e.armor
                messages.append(
                    f"{p.name} channels their strength into a devastating swing!"
                )

                if prev_armor > 0:
                    e.armor = 0  # guard always breaks
                    messages.append(
                        f"{e.name}'s guard shatters under the impact! "
                        f"(Armor reduced from {prev_armor} to 0)"
                    )
                    overflow = base_p_dmg - prev_armor
                    if overflow > 0:
                        hp_dmg = overflow * 2
                        self.apply_hp_damage(e, hp_dmg)
                        messages.append(
                            f"The force carries through, dealing {hp_dmg} HP damage to {e.name}."
                        )
                else:
                    # No armor left: just apply a big hit to HP
                    hp_dmg = base_p_dmg * 2
                    self.apply_hp_damage(e, hp_dmg)
                    messages.append(
                        f"{e.name} has no guard left and takes {hp_dmg} HP damage directly!"
                    )

                # Blocker still gains +1 Vigor for reading the attack
                e.vigor += 1
                messages.append(line_enemy_gain_vigor())
                return messages

            # Fortified enemy block (for future use, kept for symmetry)
            if e_fortify:
                messages.append(f"{p.name} strikes, but {e.name}'s fortified guard absorbs everything!")
                messages.append(f"{e.name}'s armor remains untouched. (0 Armor lost)")
                e.vigor += 1
                messages.append(line_enemy_gain_vigor())
                return messages

            # Normal Attack vs normal Block
            armor_hit = max(1, base_p_dmg // 2)
            messages.append(f"{p.name} strikes, but {e.name} braces behind its guard!")
            self.apply_armor_damage(e, armor_hit)
            e.vigor += 1
            messages.append(
                f"{e.name}'s armor absorbs part of the blow but strains under pressure. "
                f"(-{armor_hit} Armor, +1 Vigor)"
            )
            return messages

        if pa == "block" and ea == "attack":
            # Player is the blocker
            armor_hit = max(1, base_e_dmg // 2)
            if p_fortify:
                messages.append(f"{e.name} lunges, but {p.name}'s fortified stance deflects the blow!")
                messages.append(f"{p.name}'s armor remains untouched. (0 Armor lost)")
                p.vigor += 1
                messages.append(line_player_gain_vigor())
            else:
                messages.append(f"{e.name} lunges, but {p.name} raises their guard just in time!")
                self.apply_armor_damage(p, armor_hit)
                p.vigor += 1
                messages.append(
                    f"{p.name}'s armor rattles but holds. (-{armor_hit} Armor, +1 Vigor)"
                )
            return messages

        # --- Attack vs Feint / Feint vs Attack ---
        # Feinter takes critical damage.
        if pa == "attack" and ea == "feint":
            # Heavy Attack here: double on top of critical for a nasty hit
            crit_mult = 2
            if p_heavy:
                crit_mult *= 2  # heavy amplifies the critical
            crit = base_p_dmg * crit_mult
            messages.append(f"{e.name} tries something clever, but {p.name} reads it perfectly!")
            self.apply_hp_damage(e, crit)
            messages.append(f"Critical hit! {e.name} takes {crit} HP damage.")
            return messages

        if pa == "feint" and ea == "attack":
            crit = base_e_dmg * 2
            messages.append(f"{p.name} overextends with a feint and gets caught clean!")
            self.apply_hp_damage(p, crit)
            messages.append(f"Critical hit! {p.name} takes {crit} HP damage.")
            return messages

        # --- Block vs Block ---
        if pa == "block" and ea == "block":
            messages.append("Both fighters circle, shields up, waiting for an opening.")
            p.vigor += 1
            e.vigor += 1
            messages.append(line_player_gain_vigor())
            messages.append(line_enemy_gain_vigor())
            return messages

        # --- Block vs Feint / Feint vs Block ---
        # Blocker takes full damage to armor, unless using Fortify.
        if pa == "block" and ea == "feint":
            # Player is the blocker
            armor_hit = max(1, base_e_dmg)
            if p_fortify:
                messages.append(
                    f"{p.name} turtles up, and {e.name}'s feint crashes harmlessly off a fortified guard!"
                )
                messages.append(f"{p.name}'s armor takes no damage. (0 Armor lost)")
            else:
                messages.append(f"{p.name} turtles up, but {e.name}'s feint slips past the guard!")
                self.apply_armor_damage(p, armor_hit)
                messages.append(f"{p.name}'s armor takes the full force. (-{armor_hit} Armor)")
            return messages

        if pa == "feint" and ea == "block":
            # Enemy is the blocker
            armor_hit = max(1, base_p_dmg)
            if e_fortify:
                messages.append(
                    f"{e.name} braces behind a fortified shield, shrugging off {p.name}'s trick."
                )
                messages.append(f"{e.name}'s armor takes no damage. (0 Armor lost)")
            else:
                messages.append(f"{e.name} braces, but {p.name}'s feint punishes its guard!")
                self.apply_armor_damage(e, armor_hit)
                messages.append(f"{e.name}'s armor buckles under the trick. (-{armor_hit} Armor)")
            return messages

        # --- Feint vs Feint ---
        if pa == "feint" and ea == "feint":
            chip_p = max(1, base_e_dmg // 4)
            chip_e = max(1, base_p_dmg // 4)
            messages.append("Both fighters feint at the same time, stumbling into each other awkwardly.")
            self.apply_hp_damage(p, chip_p)
            self.apply_hp_damage(e, chip_e)
            messages.append(f"{p.name} takes {chip_p} chip damage.")
            messages.append(f"{e.name} takes {chip_e} chip damage.")
            return messages

        # Safety fallback (should never hit)
        messages.append("Nothing happens... (unexpected combo)")
        return messages

    def run_battle(self, player, enemy):
        """Main battle loop: handles turns until either side drops to 0 HP."""
        slow_print(f"\nYou step into the corridor...", delay=0.03)
        time.sleep(0.5)
        slow_print(f"You encountered a {enemy.name}!", delay=0.03)
        slow_print(f"{enemy.name} — HP: {enemy.health} | Armor: {enemy.armor}", delay=0.03)

        while player.health > 0 and enemy.health > 0:
            # Turn status
            print()
            slow_print(
                f"=== STATUS ===\n"
                f"{player.name} — HP: {player.health} | Armor: {player.armor} | Vigor: {player.vigor}\n"
                f"{enemy.name} — HP: {enemy.health} | Armor: {enemy.armor} | Vigor: {enemy.vigor}",
                delay=0.01
            )

            # --- Player choice ---
            slow_print("\nChoose your move:", delay=0.02)

            if player.vigor >= 2:
                # Special Vigor menu
                slow_print("You feel power surging through you. You can spend 2 Vigor:", delay=0.02)
                slow_print(
                    "1. Heavy Attack (Uses 2 Vigor) – A crushing blow that "
                    "deals greatly increased damage if it connects.",
                    delay=0.02
                )
                slow_print(
                    "2. Fortify Guard (Uses 2 Vigor) – Supercharged defense: "
                    "your guard this turn doesn’t lose armor.",
                    delay=0.02
                )
                slow_print(
                    "3. Feint – A risky fake-out. Punishes Blocks, but loses badly to direct Attacks.",
                    delay=0.02
                )

                choice = input("> ").strip().lower()
                if choice in ("1", "heavy", "heavy attack"):
                    player_action = "heavy_attack"
                    player.vigor -= 2
                    if player.vigor < 0:
                        player.vigor = 0
                elif choice in ("2", "fortify", "fortify guard"):
                    player_action = "fortify"
                    player.vigor -= 2
                    if player.vigor < 0:
                        player.vigor = 0
                elif choice in ("3", "f", "feint"):
                    player_action = "feint"
                else:
                    slow_print("You fumble your advantage and default to a basic guard...", delay=0.02)
                    player_action = "block"
            else:
                # Normal menu
                slow_print(
                    "1. Attack – A standard strike. Strong against Feints, weak into solid Blocks.",
                    delay=0.02
                )
                slow_print(
                    "2. Block – Raise your guard. Mitigates damage and can build Vigor.",
                    delay=0.02
                )
                slow_print(
                    "3. Feint – A risky fake-out. Punishes Blocks, but loses badly to Attacks.",
                    delay=0.02
                )

                choice = input("> ").strip().lower()
                if choice in ("1", "a", "attack"):
                    player_action = "attack"
                elif choice in ("2", "b", "block"):
                    player_action = "block"
                elif choice in ("3", "f", "feint"):
                    player_action = "feint"
                else:
                    slow_print("You hesitate and default to a shaky guard...", delay=0.02)
                    player_action = "block"

            # Enemy action (still simple random for now)
            enemy_action = random.choice(["attack", "block", "feint"])

            # Separate action text for player vs enemy to avoid grammar issues
            player_action_text = {
                "attack": "attack",
                "block": "raise your guard",
                "feint": "feint",
                "heavy_attack": "unleash a heavy attack",
                "fortify": "brace behind a fortified guard",
            }

            enemy_action_text = {
                "attack": "attacks",
                "block": "raises its guard",
                "feint": "feints",
                "heavy_attack": "unleashes a heavy attack",
                "fortify": "braces behind a fortified guard",
            }

            print()
            slow_print(
                f"You {player_action_text[player_action]} and the {enemy.name} "
                f"{enemy_action_text[enemy_action]}...",
                delay=0.03,
            )
            time.sleep(0.3)

            # Resolve the turn
            outcome_lines = self.resolve_turn(player, enemy, player_action, enemy_action)
            for line in outcome_lines:
                slow_print(line, delay=0.02)
                time.sleep(0.05)

            # Short pause before next round
            time.sleep(0.3)

            # Check for defeat
            if player.health <= 0 or enemy.health <= 0:
                break

        # End of battle
        print()
        if player.health <= 0 and enemy.health <= 0:
            slow_print("Both you and your foe collapse to the ground...", delay=0.03)
            return "double_ko"
        elif player.health <= 0:
            slow_print("Your vision fades. The dungeon claims another soul.", delay=0.03)
            return "player_dead"
        else:
            slow_print(f"The {enemy.name} falls. You stand victorious.", delay=0.03)
            # handle gold loot if enemy has gold range
            gold_min = getattr(enemy, "gold_min", 0)
            gold_max = getattr(enemy, "gold_max", 0)
            if gold_max > gold_min:
                gold_loot = random.randint(gold_min, gold_max)
            else:
                gold_loot = gold_min
            player.money += gold_loot
            if gold_loot > 0:
                slow_print(f"You loot {gold_loot} gold.", delay=0.03)
            return "enemy_dead"
