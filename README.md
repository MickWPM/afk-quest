# afk-quest

Simple RPG to be iteratively developed upon. The intent is for this to provide a little bored afk fun but also serve as a tool to practice development using test frameworks. Note this application is built under the following paradigm:
- Plan and architecture developed
- Class requirements developed and test range defined
- Gemini AI leveraged to construct main code files and test coverage
- Code files edited to ensure desired functionality is achieved

## Concept
Player creates a character and defines a name. The player chooses options:
- Explore current area
- Move to new area
- Rest
- Look for a fight

These actions allow players to go to new areas, gain loot and equipment and experience.

The conceptual approach:

~~**Phase 1:**~~ **Complete!**
- ~~Develop character system (character.py)~~
    - ~~Creation and save/loading~~
    - ~~Attribute tracking (max hp based on level * 15, exp to next level baesd on level * 10)~~
    - ~~Exp gain (Including checking for level, auto overflowing exp to next level)~~
    - ~~Damage (Deducting damage from hp, Checking for death and flagging it)~~
    - ~~Healing (negative damage)~~
    - ~~Equipment slots (gold count - functional, Weapon, Armour, Item - All are None for now)~~
    - ~~Character summary (Name, Level, Gold, Equipment)~~


- ~~Game loop (game.py)~~
    - ~~Auto load character from file (if it exists)~~
    - ~~Give user option to continue or start a new character (continue not available if no existing character)~~
    - ~~Allow user to add exp, damage character, heal character, add gold. After each interaction, report player summary~~
    - ~~Allow user to quit - on quit, save character to file~~


- ~~Develop test framework~~
    - ~~Testing all points above for character~~

~~**Phase 2:**~~ **Complete!**
- ~~Combat update~~
    - ~~Allow character to look for a fight~~
    - ~~Enemy (enemy.py) includes hp, attack, loot table. Enemy also includes damage application methods and is dead check.~~
    - ~~Enemy encounter drawn from a master manager (enemy_manager.py) - This should be initialised within each zone instance and accessed through the zone object.~~
    - ~~Player class updated to have attack stat (Check if weapon exists, if not fallback is 1dmg with fists - in this case weapon will always be None so it will always fall back to fists. No logic required for weapons yet)~~
    - ~~Player class updated to consider armour in damage function. No armour exists yet so if armour is None, fallback is 0 damage reduction. No logic required for armour yet, stop after checking none and returning the 0 reduction.~~
    - ~~Combat auto resolved. Each round the damage is randomised between 0 and damage and applied to both enemy and player. Each round results is presented to player, subsequent round does not occur until player presses enter. No option to flee.~~
    - ~~If enemy dies, loot is randomised (implementation TBC). If player dies, player death screen is displayed.~~

- ~~Add testing for introduced logic~~

**Phase 2b** _In Progress_
- Already reading data locally; offload to publicly viewable google sheets instance.
- Update test suite to cover the amended load functionality including increased scope

**Phase 3:**
- Itemisation update
    - Weapon, item and armour functionality developed (weapon adds dmg when getting attack value, armour provides dmg reduction during on damage calculations, item functionlaity intent is to support epxloration activities (eg. a rope to climb down into an area for unique loot) and potential other effects (eg. regen 1hp every 3 combat rounds) - No item functionlity is implemented in this update)
    - Item equipping logic implemented. If weapon is equipped over an existing weapon, the replaced item is "cashed in". Likewise if a loot item is not equipped, it is "cashed in" based on the item value.

- Add testing for introduced logic

**Phase 4:**
- Exploration update
    - Allow character to explore the current area (random chance of finding gold/loot/fight etc)
    - Allow character to move to new area (Connected zone graph) (zone.py, zone_manager.py - note zone info only contains name for now)
    - Allow character to rest in current area (Heal 1 hp, chance of getting attacked)
    - Allow character to  look for fight (per Phase 2)

- Add testing for introduced logic

**Future phases:**
- Real exploration: Connected zones are not known, can be discovered by exploration. Once exploration finds a zone connection (random chance) it is known and opens up that option in future
- Inventory update: Items are no longer auto cashed in, player has an inventory and can choose items to be equipped. Old items are moved to inventory
- Trade update: Some zones may have shops that will allow buying/selling of items
- Real item functionality: Add in the item functionlity, both combat and exploration
- Database update: Move all storage (character, zone, items, enemies etc) to database
- Connected update: Refactor to be server based; individual users are given a unique access code to access/create thier characters
