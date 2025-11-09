# Combat.py

import time
import random
from UI import slow_print


class Combat:
    # ------------------------
    # BASIC DAMAGE HELPERS
    # ------------------------
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

    def _describe_vigor_gain(self, a, b):
        """Helper to describe vigor gains for two combatants."""
        return [
            f"{a.name} steels their resolve. (+1 Vigor)",
            f"{b.name} looks more focused. (+1 Vigor)",
        ]

    # ------------------------------------------------------------------
    # MATCHUP HELPERS
    # Each of these handles ONE (effective_action_player, effective_action_enemy) combo
    # ------------------------------------------------------------------

    # --- Attack vs Attack (including heavy vs normal) ---
    def _attack_vs_attack(self, p, e, base_p_dmg, base_e_dmg, p_heavy, e_heavy):
        """
        Special rule:

        - If one side uses Heavy Attack and the other uses a normal Attack:
          the Heavy user deals their BASE damage to the other's armor (with
          possible spill into HP). This replaces the usual "parry" (no damage).

        - If both use Heavy Attack OR both use normal Attack:
          it's a parry: no damage, both gain +1 Vigor.
        """
        messages = []

        # Player heavy vs enemy normal
        if p_heavy and not e_heavy:
            messages.append(
                f"{e.name} steps in with a standard strike, but "
                f"{p.name}'s heavy swing blows straight through!"
            )
            self._apply_heavy_vs_normal_damage(attacker=p, defender=e, base_dmg=base_p_dmg, messages=messages)
            return messages

        # Enemy heavy vs player normal
        if e_heavy and not p_heavy:
            messages.append(
                f"{p.name} rushes in with a quick attack, but "
                f"{e.name}'s heavy swing smashes straight through!"
            )
            self._apply_heavy_vs_normal_damage(attacker=e, defender=p, base_dmg=base_e_dmg, messages=messages)
            return messages

        # Normal vs normal OR heavy vs heavy: parry
        messages.append("Steel clashes against steel as both sides lunge in!")
        messages.append("No clean hit is landed, but tension rises.")
        p.vigor += 1
        e.vigor += 1
        messages.extend(self._describe_vigor_gain(p, e))
        return messages

    def _apply_heavy_vs_normal_damage(self, attacker, defender, base_dmg, messages):
        """Shared helper: heavy vs normal attack, base damage to armor/HP."""
        prev_armor = defender.armor
        prev_health = defender.health

        # heavy vs attack: base damage only (no 2x), into armor/HP
        self.apply_armor_damage(defender, base_dmg)

        armor_loss = prev_armor - defender.armor
        hp_loss = prev_health - defender.health

        if prev_armor > 0 and defender.armor > 0:
            messages.append(
                f"{defender.name}'s armor staggers under the weight of the blow. "
                f"(-{armor_loss} Armor)"
            )
        elif prev_armor > 0 and defender.armor == 0:
            if hp_loss > 0:
                messages.append(
                    f"{defender.name}'s armor shatters and the strike bites into flesh. "
                    f"(-{armor_loss} Armor, -{hp_loss} HP)"
                )
            else:
                messages.append(
                    f"{defender.name}'s armor shatters, leaving them exposed. "
                    f"(-{armor_loss} Armor)"
                )
        else:
            messages.append(
                f"{defender.name} has no guard left and takes {hp_loss} HP damage directly!"
            )

    # --- Attack vs Block (player attacking, enemy blocking) ---
    def _attack_vs_block(self, p, e, base_p_dmg, p_heavy, e_fortify):
        messages = []

        # Player Heavy Attack vs enemy Block
        if p_heavy:
            prev_armor = e.armor
            messages.append(f"{p.name} channels their strength into a devastating swing!")

            # Fortified block: perfect guard, even against heavy
            if e_fortify:
                messages.append(
                    f"{e.name} braces behind a fortified guard, absorbing even the heavy strike!"
                )
                messages.append(f"{e.name}'s armor remains untouched. (0 Armor lost)")
                e.vigor += 1
                messages.append(f"{e.name} looks more focused. (+1 Vigor)")
                return messages

            # Normal heavy vs block
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
            messages.append(f"{e.name} looks more focused. (+1 Vigor)")
            return messages

        # Normal Attack vs Block
        armor_hit = max(1, base_p_dmg // 2)
        messages.append(f"{p.name} strikes, but {e.name} braces behind its guard!")

        if e_fortify:
            messages.append(
                f"{e.name}'s fortified stance turns the blow aside. (0 Armor lost)"
            )
            e.vigor += 1
            messages.append(f"{e.name} looks more focused. (+1 Vigor)")
            return messages

        prev_armor = e.armor
        prev_health = e.health
        self.apply_armor_damage(e, armor_hit)
        e.vigor += 1

        armor_loss = prev_armor - e.armor
        hp_loss = prev_health - e.health

        if prev_armor <= 0:
            messages.append(
                f"{e.name} has no armor left; the blow crashes into its body. "
                f"(-{hp_loss} HP, +1 Vigor)"
            )
        elif e.armor > 0:
            messages.append(
                f"{e.name}'s armor absorbs part of the blow but strains under pressure. "
                f"(-{armor_loss} Armor, +1 Vigor)"
            )
        else:
            if hp_loss > 0:
                messages.append(
                    f"{e.name}'s armor shatters, and the strike bites into flesh. "
                    f"(-{armor_loss} Armor, -{hp_loss} HP, +1 Vigor)"
                )
            else:
                messages.append(
                    f"{e.name}'s armor shatters, leaving it exposed. "
                    f"(-{armor_loss} Armor, +1 Vigor)"
                )

        return messages

    # --- Block vs Attack (enemy attacking, player blocking) ---
    def _block_vs_attack(self, p, e, base_e_dmg, e_heavy, p_fortify):
        messages = []
        armor_hit = max(1, base_e_dmg // 2)

        # Enemy Heavy Attack vs player Block
        if e_heavy:
            prev_armor = p.armor
            messages.append(f"{e.name} swings with a brutal, committed strike!")

            if p_fortify:
                messages.append(
                    f"{p.name}'s fortified guard absorbs even the heavy blow!"
                )
                messages.append(f"{p.name}'s armor remains untouched. (0 Armor lost)")
                p.vigor += 1
                messages.append(f"{p.name} steels their resolve. (+1 Vigor)")
                return messages

            if prev_armor > 0:
                p.armor = 0
                messages.append(
                    f"{p.name}'s guard shatters under the impact! "
                    f"(Armor reduced from {prev_armor} to 0)"
                )
                overflow = base_e_dmg - prev_armor
                if overflow > 0:
                    hp_dmg = overflow * 2
                    self.apply_hp_damage(p, hp_dmg)
                    messages.append(
                        f"The force carries through, dealing {hp_dmg} HP damage to {p.name}."
                    )
            else:
                # No armor left: just HP
                hp_dmg = base_e_dmg * 2
                self.apply_hp_damage(p, hp_dmg)
                messages.append(
                    f"{p.name} has no guard left and takes {hp_dmg} HP damage directly!"
                )

            p.vigor += 1
            messages.append(f"{p.name} steels their resolve. (+1 Vigor)")
            return messages

        # Normal Attack vs Block
        if p_fortify:
            messages.append(f"{e.name} lunges, but {p.name}'s fortified stance deflects the blow!")
            messages.append(f"{p.name}'s armor remains untouched. (0 Armor lost)")
            p.vigor += 1
            messages.append(f"{p.name} steels their resolve. (+1 Vigor)")
            return messages

        messages.append(f"{e.name} lunges, but {p.name} raises their guard just in time!")

        prev_armor = p.armor
        prev_health = p.health
        self.apply_armor_damage(p, armor_hit)
        p.vigor += 1

        armor_loss = prev_armor - p.armor
        hp_loss = prev_health - p.health

        if prev_armor <= 0:
            messages.append(
                f"{p.name} has no armor left; the blow crashes into their body. "
                f"(-{hp_loss} HP, +1 Vigor)"
            )
        elif p.armor > 0:
            messages.append(
                f"{p.name}'s armor rattles but holds. (-{armor_loss} Armor, +1 Vigor)"
            )
        else:
            if hp_loss > 0:
                messages.append(
                    f"{p.name}'s armor shatters, and pain follows through. "
                    f"(-{armor_loss} Armor, -{hp_loss} HP, +1 Vigor)"
                )
            else:
                messages.append(
                    f"{p.name}'s armor shatters under the blow. "
                    f"(-{armor_loss} Armor, +1 Vigor)"
                )

        return messages

    # --- Attack vs Feint / Feint vs Attack ---
    def _attack_vs_feint(self, p, e, base_p_dmg, p_heavy):
        messages = []
        crit_mult = 2
        if p_heavy:
            crit_mult *= 2  # Heavy makes crit even worse
        crit = base_p_dmg * crit_mult
        messages.append(f"{e.name} tries something clever, but {p.name} reads it perfectly!")
        self.apply_hp_damage(e, crit)
        messages.append(f"Critical hit! {e.name} takes {crit} HP damage.")
        return messages

    def _feint_vs_attack(self, p, e, base_e_dmg, e_heavy):
        messages = []
        crit_mult = 2
        if e_heavy:
            crit_mult *= 2
        crit = base_e_dmg * crit_mult
        messages.append(f"{p.name} overextends with a feint and gets caught clean!")
        self.apply_hp_damage(p, crit)
        messages.append(f"Critical hit! {p.name} takes {crit} HP damage.")
        return messages

    # --- Block vs Block ---
    def _block_vs_block(self, p, e):
        messages = []
        messages.append("Both fighters circle, shields up, waiting for an opening.")
        p.vigor += 1
        e.vigor += 1
        messages.extend(self._describe_vigor_gain(p, e))
        return messages

    # --- Block vs Feint / Feint vs Block ---
    def _block_vs_feint(self, p, e, base_e_dmg, p_fortify):
        messages = []
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

    def _feint_vs_block(self, p, e, base_p_dmg, e_fortify):
        messages = []
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
    def _feint_vs_feint(self, p, e, base_p_dmg, base_e_dmg):
        messages = []
        chip_p = max(1, base_e_dmg // 4)
        chip_e = max(1, base_p_dmg // 4)
        messages.append("Both fighters feint at the same time, stumbling into each other awkwardly.")
        self.apply_hp_damage(p, chip_p)
        self.apply_hp_damage(e, chip_e)
        messages.append(f"{p.name} takes {chip_p} chip damage.")
        messages.append(f"{e.name} takes {chip_e} chip damage.")
        return messages

    # ------------------------
    # TURN RESOLUTION DISPATCHER
    # ------------------------
    def resolve_turn(self, player, enemy, player_action, enemy_action):
        """
        Dispatcher: figures out which matchup helper to call
        and returns a list of message strings for that turn.
        """
        p = player
        e = enemy

        # Flags for specials
        p_heavy = (player_action == "heavy_attack")
        p_fortify = (player_action == "fortify")
        e_heavy = (enemy_action == "heavy_attack")
        e_fortify = (enemy_action == "fortify")

        # Map heavy/fortify to their base action for the RPS logic
        def effective_action(action, is_heavy, is_fortify):
            if is_heavy:
                return "attack"
            if is_fortify:
                return "block"
            return action

        pa = effective_action(player_action, p_heavy, p_fortify)
        ea = effective_action(enemy_action, e_heavy, e_fortify)

        # Base (non-multiplied) damage values
        base_p_dmg = p.damage
        base_e_dmg = e.damage

        # Dispatch table for (player_action, enemy_action)
        handlers = {
            ("attack", "attack"): lambda: self._attack_vs_attack(
                p, e, base_p_dmg, base_e_dmg, p_heavy, e_heavy
            ),
            ("attack", "block"): lambda: self._attack_vs_block(
                p, e, base_p_dmg, p_heavy, e_fortify
            ),
            ("block", "attack"): lambda: self._block_vs_attack(
                p, e, base_e_dmg, e_heavy, p_fortify
            ),
            ("attack", "feint"): lambda: self._attack_vs_feint(
                p, e, base_p_dmg, p_heavy
            ),
            ("feint", "attack"): lambda: self._feint_vs_attack(
                p, e, base_e_dmg, e_heavy
            ),
            ("block", "block"): lambda: self._block_vs_block(p, e),
            ("block", "feint"): lambda: self._block_vs_feint(
                p, e, base_e_dmg, p_fortify
            ),
            ("feint", "block"): lambda: self._feint_vs_block(
                p, e, base_p_dmg, e_fortify
            ),
            ("feint", "feint"): lambda: self._feint_vs_feint(
                p, e, base_p_dmg, base_e_dmg
            ),
        }

        handler = handlers.get((pa, ea))
        if handler is not None:
            return handler()

        # Safety fallback (should never hit)
        return ["Nothing happens... (unexpected combo)"]

    # ------------------------
    # INPUT / AI
    # ------------------------
    def _get_player_action_with_vigor(self, player):
        """Menu when the player has enough Vigor for specials."""
        slow_print("You feel power surging through you. You can spend 2 Vigor:", delay=0.02)
        slow_print(
            "1. Heavy Attack (Uses 2 Vigor) – A crushing blow that "
            "deals greatly increased damage if it connects.",
            delay=0.02,
        )
        slow_print(
            "2. Fortify Guard (Uses 2 Vigor) – Supercharged defense: "
            "your guard this turn doesn’t lose armor.",
            delay=0.02,
        )
        slow_print(
            "3. Feint – A risky fake-out. Punishes Blocks, but loses badly to direct Attacks.",
            delay=0.02,
        )

        choice = input("> ").strip().lower()
        if choice in ("1", "heavy", "heavy attack"):
            player.vigor = max(0, player.vigor - 2)
            return "heavy_attack"
        if choice in ("2", "fortify", "fortify guard"):
            player.vigor = max(0, player.vigor - 2)
            return "fortify"
        if choice in ("3", "f", "feint"):
            return "feint"

        slow_print("You fumble your advantage and default to a basic guard...", delay=0.02)
        return "block"

    def _get_player_action_basic(self, player):
        """Menu when the player does not have enough Vigor for specials."""
        slow_print(
            "1. Attack – A standard strike. Strong against Feints, weak into solid Blocks.",
            delay=0.02,
        )
        slow_print(
            "2. Block – Raise your guard. Mitigates damage and can build Vigor.",
            delay=0.02,
        )
        slow_print(
            "3. Feint – A risky fake-out. Punishes Blocks, but loses badly to Attacks.",
            delay=0.02,
        )

        choice = input("> ").strip().lower()
        if choice in ("1", "a", "attack"):
            return "attack"
        if choice in ("2", "b", "block"):
            return "block"
        if choice in ("3", "f", "feint"):
            return "feint"

        slow_print("You hesitate and default to a shaky guard...", delay=0.02)
        return "block"

    def _get_player_action(self, player):
        """Ask the player for an action and return the logical action string."""
        slow_print("\nChoose your move:", delay=0.02)

        if player.vigor >= 2:
            return self._get_player_action_with_vigor(player)

        return self._get_player_action_basic(player)

    def _get_enemy_action(self, enemy):
        """
        Simple enemy AI:
        - If it has 2+ Vigor, it has a chance to use Heavy Attack or Fortify.
        - Otherwise, picks between Attack / Block / Feint.
        """
        if enemy.vigor >= 2:
            # Weighted choice: heavy 40%, fortify 30%, feint 30%
            roll = random.random()
            if roll < 0.4:
                enemy.vigor = max(0, enemy.vigor - 2)
                return "heavy_attack"
            if roll < 0.7:
                enemy.vigor = max(0, enemy.vigor - 2)
                return "fortify"
            return "feint"

        return random.choice(["attack", "block", "feint"])

    # ------------------------
    # MAIN BATTLE LOOP
    # ------------------------
    def run_battle(self, player, enemy):
        """Main battle loop: handles turns until either side drops to 0 HP."""
        slow_print("\nYou step into the corridor...", delay=0.03)
        time.sleep(0.5)
        slow_print(f"You encountered a {enemy.name}!", delay=0.03)
        slow_print(f"{enemy.name} — HP: {enemy.health} | Armor: {enemy.armor}", delay=0.03)

        while player.health > 0 and enemy.health > 0:
            # Turn status
            print()
            slow_print(
                "=== STATUS ===\n"
                f"{player.name} — HP: {player.health} | Armor: {player.armor} | Vigor: {player.vigor}\n"
                f"{enemy.name} — HP: {enemy.health} | Armor: {enemy.armor} | Vigor: {enemy.vigor}",
                delay=0.01,
            )

            # Player choice
            player_action = self._get_player_action(player)

            # Enemy choice
            enemy_action = self._get_enemy_action(enemy)

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
        if player.health <= 0:
            slow_print("Your vision fades. The dungeon claims another soul.", delay=0.03)
            return "player_dead"

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