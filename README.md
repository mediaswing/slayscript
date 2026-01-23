================================================================================
                              SLAYSCRIPT
                        Cast spells, slay bugs.
================================================================================

A programming language inspired by Harry Potter and Buffy the Vampire Slayer,
featuring text-to-speech, networking, HTML/CSS generation, file I/O, MySQL
database support, RPG gameplay mechanics, and enterprise Microsoft 365 /
Entra ID administration.

File extension: .slay

================================================================================
                            QUICK START
================================================================================

RUNNING FROM SOURCE (requires Python 3.7+):

    python -m slayscript examples/hello_world.slay    Run a file
    python -m slayscript                              Start REPL
    python -m slayscript -c "scribe_line('Hello')"    Run inline code

BUILDING AN EXECUTABLE:

    Windows (Command Prompt):   build.bat
    Windows (PowerShell):       .\build.ps1
    Any platform:               python build.py

    After building, the executable is at: dist/slayscript.exe (Windows)
                                          dist/slayscript     (Mac/Linux)

RUNNING THE COMPILED EXECUTABLE:

    Windows:    dist\slayscript.exe examples\hello_world.slay
    Mac/Linux:  ./dist/slayscript examples/hello_world.slay

================================================================================
                            DEPENDENCIES
================================================================================

Install dependencies with:  pip install -r requirements.txt

Required:
    - pyttsx3                   Text-to-speech engine
    - msal                      Microsoft Authentication Library (for M365)
    - requests                  HTTP client (for M365)
    - mysql-connector-python    MySQL database support (for Oracle functions)

For building executables:
    - pyinstaller    (installed automatically by build scripts)

================================================================================
                            LANGUAGE SYNTAX
================================================================================

VARIABLES:
    conjure x as 5                  Variable declaration
    summon name as "Buffy"          Alternative syntax
    transmute x as x + 1            Reassignment
    const prophecy PI as 3.14       Constant (cannot be changed)
    vanquish x                      Delete variable

DATA TYPES:
    scroll "text"                   String
    rune 42                         Integer
    potion 3.14                     Float
    charm true / charm false        Boolean
    tome [1, 2, 3]                  List
    grimoire {"key": "value"}      Dictionary
    void                            Null

FUNCTIONS:
    spell fireball(target) {
        scribe_line("Casting at " + target)
        cast "success"              ~ Return statement
    }

    incantation greeting(name) {    ~ Auto-speaks return value
        cast "Hello " + name
    }

CONTROL FLOW:
    prophecy reveals x > 5 {        ~ If
        scribe_line("Big")
    }
    otherwise prophecy x > 0 {      ~ Elif
        scribe_line("Small")
    }
    fate decrees {                  ~ Else
        scribe_line("Zero")
    }

    patrol until count > 10 {       ~ While (loops while condition is FALSE)
        transmute count as count + 1
    }

    hunt each item in collection {  ~ For each
        scribe_line(item)
    }

OPERATORS:
    Comparison:  is, isnt, exceeds, under, atleast, atmost
    Logical:     and, or, not
    Arithmetic:  +, -, *, /, %, **

COMMENTS:
    ~ Single line comment
    ~~ Multi-line
       comment ~~

================================================================================
                          BUILT-IN FUNCTIONS
================================================================================

TEXT-TO-SPEECH:
    speak_spell(text)               Speak text aloud
    whisper_spell(text)             Speak quietly
    shout_spell(text)               Speak loudly
    change_voice(id)                Switch voice (0, 1, 2...)
    set_speech_rate(rate)           Adjust speed (words per minute)

NETWORKING:
    summon_portal(host, port)       Connect to server
    open_hellmouth(port)            Start server
    send_owl(portal, message)       Send data
    receive_owl(portal)             Receive data
    close_portal(portal)            Close connection
    await_visitor(hellmouth)        Accept connection

HTML/CSS GENERATION:
    conjure_canvas(title)           Create HTML document
    enchant_element(tag, content, attrs)   Create element
    enchant_style(selector, props)  Create CSS rule
    append_to_canvas(canvas, elem)  Add element to body
    add_style_to_canvas(canvas, style)     Add CSS
    weave_page(canvas)              Generate HTML string
    scribe_page(canvas, filename)   Write HTML to file
    summon_browser(filename)        Open in browser

INPUT/OUTPUT:
    scribe_line(text)               Print with newline
    scribe(text)                    Print without newline
    prophecy_input(prompt)          Read user input

UTILITIES:
    measure(collection)             Get length
    transform_to_rune(val)          Convert to integer
    transform_to_scroll(val)        Convert to string
    transform_to_potion(val)        Convert to float
    random_fate(min, max)           Random number (inclusive)
    slumber(seconds)                Sleep
    range(start, end, step)         Generate number list
    append(list, item)              Add to list
    remove(list, item)              Remove from list
    keys(dict)                      Get dictionary keys
    values(dict)                    Get dictionary values
    type_of(value)                  Get type name

================================================================================
                    FILE I/O (Ancient Scrolls Theme)
================================================================================

SlayScript provides file operations using folklore-inspired terminology,
treating files as ancient scrolls and archives.

BASIC FILE OPERATIONS:
    inscribe_scroll(path, content)  Write content to file (overwrites)
    chronicle_scroll(path, content) Append content to file
    decipher_scroll(path)           Read entire file contents
    divine_lines(path)              Read file as list of lines
    scroll_exists(path)             Check if file exists (returns charm)
    banish_scroll(path)             Delete a file

FILE HANDLE OPERATIONS (for more control):
    unroll_scroll(path, mode)       Open file ("read", "write", "append")
    seal_scroll(handle)             Close an open file handle
    read_runes(handle, [num_chars]) Read from open file handle
    etch_runes(handle, content)     Write to open file handle

EXAMPLE - Writing and reading a scroll:
    ~ Write a new scroll
    inscribe_scroll("legend.txt", "In ages past, heroes walked the land.")

    ~ Read it back
    conjure contents as decipher_scroll("legend.txt")
    scribe_line(contents)

    ~ Append to chronicle
    chronicle_scroll("legend.txt", "\nA new hero emerges.")

    ~ Read as lines
    conjure lines as divine_lines("legend.txt")
    hunt each line in lines {
        scribe_line(line)
    }

    ~ Clean up
    banish_scroll("legend.txt")

EXAMPLE - Using file handles:
    conjure scroll as unroll_scroll("notes.txt", "write")
    etch_runes(scroll, "Line 1\n")
    etch_runes(scroll, "Line 2\n")
    seal_scroll(scroll)

    conjure reader as unroll_scroll("notes.txt", "read")
    conjure text as read_runes(reader)
    seal_scroll(reader)

================================================================================
                    MySQL DATABASE (Oracle of Delphi Theme)
================================================================================

SlayScript provides MySQL database support using mythology-inspired terminology,
treating database connections as consulting an ancient oracle.

Requires: pip install mysql-connector-python

CONNECTION:
    awaken_oracle(host, user, password, database, [port])
        Connect to MySQL database (default port: 3306)

    dismiss_oracle(connection)
        Close the database connection

QUERYING (SELECT):
    consult_oracle(conn, query, [params])
        Execute SELECT, return all rows as tome of grimoires

    divine_one(conn, query, [params])
        Execute SELECT, return first row as grimoire (or void)

MODIFYING (INSERT/UPDATE/DELETE):
    decree_oracle(conn, query, [params])
        Execute INSERT/UPDATE/DELETE, return affected row count

    last_prophecy_id(connection)
        Get the last auto-increment ID from INSERT

TRANSACTIONS (Rituals):
    begin_ritual(connection)        Start a transaction
    complete_ritual(connection)     Commit the transaction
    abandon_ritual(connection)      Rollback the transaction

EXAMPLE - Basic database operations:
    ~ Connect to the Oracle
    conjure oracle as awaken_oracle("localhost", "root", "password", "mydb")

    ~ Create a table
    decree_oracle(oracle, "
        CREATE TABLE IF NOT EXISTS heroes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            level INT
        )
    ")

    ~ Insert with parameters (prevents SQL injection)
    decree_oracle(oracle, "INSERT INTO heroes (name, level) VALUES (%s, %s)",
                  tome ["Aragorn", 15])
    conjure hero_id as last_prophecy_id(oracle)

    ~ Query all heroes
    conjure heroes as consult_oracle(oracle, "SELECT * FROM heroes")
    hunt each hero in heroes {
        scribe_line(hero["name"] + " - Level " + transform_to_scroll(hero["level"]))
    }

    ~ Query one hero
    conjure mage as divine_one(oracle, "SELECT * FROM heroes WHERE name = %s",
                               tome ["Gandalf"])

    ~ Use a transaction
    begin_ritual(oracle)
    decree_oracle(oracle, "UPDATE heroes SET level = level + 1 WHERE level < 10")
    complete_ritual(oracle)  ~ Or abandon_ritual(oracle) to rollback

    ~ Disconnect
    dismiss_oracle(oracle)

================================================================================
                    GAMEPLAY FEATURES (Quest/Legend Theme)
================================================================================

SlayScript includes RPG gameplay mechanics using quest and legend terminology,
perfect for creating text adventures and games.

CHARACTER CREATION:
    forge_hero(name, [class], [level])
        Create a hero with RPG stats. Classes: adventurer, warrior, mage,
        rogue, ranger, cleric, paladin, bard. Returns a grimoire with:
        name, class, level, experience, health, max_health, mana, max_mana,
        strength, agility, wisdom, vitality, gold, inventory, equipped, alive

    forge_creature(name, health, damage, [loot])
        Create an enemy/NPC with health, damage, and optional loot tome

DICE AND CHANCE:
    roll_destiny(sides, [count], [modifier])
        Roll dice - roll_destiny(20) for d20, roll_destiny(6, 3, 2) for 3d6+2

    encounter_chance(percent)
        Random percentage check (0-100), returns charm

    choose_fate(options)
        Randomly select one item from a tome

COMBAT:
    inflict_wound(target, damage)
        Deal damage to hero or creature, updates health and alive status

    restore_vigor(target, amount)
        Heal a hero or creature (capped at max_health)

    check_fate(target)
        Check if hero or creature is still alive (returns charm)

    claim_loot(creature)
        Collect loot from defeated creature (must be dead)

PROGRESSION:
    gain_experience(hero, amount)
        Award XP with automatic level-up (100 XP per level)
        Level-up boosts all stats

    bestow_artifact(hero, item)
        Add an item to hero's inventory

SAVE/LOAD:
    saga_save(data, path)
        Save any data (hero, game state) to JSON file

    saga_load(path)
        Load game state from JSON file

EXAMPLE - Simple combat encounter:
    ~ Create hero and monster
    conjure hero as forge_hero("Aldric", "warrior", 1)
    conjure goblin as forge_creature("Goblin", 30, 8, tome ["Gold Coin", "Dagger"])

    scribe_line("A " + goblin["name"] + " appears!")

    ~ Combat loop
    patrol until (not check_fate(hero)) or (not check_fate(goblin)) {
        ~ Hero attacks
        conjure attack_roll as roll_destiny(20)
        prophecy reveals attack_roll atleast 10 {
            conjure damage as roll_destiny(6, 1, hero["strength"])
            inflict_wound(goblin, damage)
            scribe_line("Hit! Dealt " + transform_to_scroll(damage) + " damage!")
        } fate decrees {
            scribe_line("Miss!")
        }

        prophecy reveals not check_fate(goblin) {
            break
        }

        ~ Goblin attacks
        prophecy reveals roll_destiny(20) atleast 12 {
            inflict_wound(hero, goblin["damage"])
            scribe_line("Goblin strikes for " + transform_to_scroll(goblin["damage"]))
        }
    }

    ~ Victory?
    prophecy reveals check_fate(hero) {
        scribe_line("Victory!")
        conjure loot as claim_loot(goblin)
        hunt each item in loot {
            bestow_artifact(hero, item)
            scribe_line("Got: " + item)
        }
        gain_experience(hero, 50)
    }

EXAMPLE - Save and load game:
    conjure game_state as grimoire {
        "hero": hero,
        "location": "Dark Forest",
        "chapter": 1
    }
    saga_save(game_state, "savegame.json")

    ~ Later...
    conjure loaded as saga_load("savegame.json")
    scribe_line("Welcome back, " + loaded["hero"]["name"])

================================================================================
               MICROSOFT 365 / ENTRA ID ADMINISTRATION (Enterprise)
================================================================================

SlayScript includes enterprise administration capabilities for Microsoft 365
and Entra ID (formerly Azure AD) using the Microsoft Graph API.

SETUP REQUIRED:
    1. Register an application in Azure AD (Entra ID Admin Center)
    2. Grant Microsoft Graph API permissions (Application type):
       - User.ReadWrite.All
       - Group.ReadWrite.All
       - Directory.ReadWrite.All
       - Organization.Read.All
       - (Add more as needed for your use case)
    3. Create a client secret
    4. Note your Tenant ID, Client ID, and Client Secret

CONNECTION:
    summon_azure_realm(tenant_id, client_id, client_secret)
        Connect to Azure/M365 and authenticate

    banish_azure_realm()
        Disconnect from Azure/M365

USER MANAGEMENT:
    divine_users([top])             List users (default: 100)
    divine_user(user_id)            Get a specific user by ID or UPN
    conjure_user(display_name, mail_nickname, upn, password)
                                    Create a new user
    transmute_user(user_id, properties)
                                    Update user properties (pass grimoire)
    vanquish_user(user_id)          Delete a user
    silence_user(user_id)           Disable a user account
    awaken_user(user_id)            Enable a user account
    reset_user_ward(user_id, new_password)
                                    Reset a user's password

GROUP MANAGEMENT:
    divine_groups([top])            List groups (default: 100)
    divine_group(group_id)          Get a specific group
    conjure_group(display_name, mail_nickname, [description])
                                    Create a security group
    vanquish_group(group_id)        Delete a group
    divine_group_members(group_id)  Get members of a group
    bind_to_group(group_id, user_id)
                                    Add a user to a group
    unbind_from_group(group_id, user_id)
                                    Remove a user from a group

LICENSE MANAGEMENT:
    divine_licenses()               List available licenses/SKUs
    divine_user_licenses(user_id)   Get licenses assigned to a user
    bestow_license(user_id, sku_id) Assign a license to a user
    revoke_license(user_id, sku_id) Remove a license from a user

DIRECTORY & ORGANIZATION:
    divine_organization()           Get tenant/organization details
    divine_domains()                List domains in the tenant
    divine_roles()                  List directory roles
    divine_role_members(role_id)    Get members of a directory role
    divine_apps([top])              List application registrations
    divine_service_principals([top])
                                    List service principals

SECURITY & AUDIT:
    divine_signin_logs([top])       Get sign-in logs (requires AAD Premium)
    divine_conditional_policies()   List conditional access policies

EXAMPLE - List all users:
    summon_azure_realm(tenant_id, client_id, secret)
    conjure users as divine_users(50)
    hunt each user in users {
        scribe_line(user["displayName"] + " - " + user["userPrincipalName"])
    }
    banish_azure_realm()

EXAMPLE - Create and manage a user:
    summon_azure_realm(tenant_id, client_id, secret)

    ~ Create user
    conjure new_user as conjure_user(
        "John Slayer",
        "johnslayer",
        "john.slayer@contoso.com",
        "TempPassword123!"
    )

    ~ Disable the user
    silence_user(new_user["id"])

    ~ Re-enable
    awaken_user(new_user["id"])

    ~ Assign a license
    bestow_license(new_user["id"], "sku-id-here")

    ~ Add to a group
    bind_to_group("group-id", new_user["id"])

    banish_azure_realm()

================================================================================
                            EXAMPLE PROGRAMS
================================================================================

examples/hello_world.slay     Basic syntax demonstration
examples/fibonacci.slay       Recursion and loops
examples/vampire_hunt.slay    Text adventure game
examples/network_chat.slay    Client/server networking
examples/web_page.slay        HTML/CSS generation
examples/tts_demo.slay        Text-to-speech features
examples/m365_admin.slay      Microsoft 365 / Entra ID administration
examples/file_scrolls.slay    File I/O operations (Ancient Scrolls theme)
examples/oracle_database.slay MySQL database operations (Oracle theme)
examples/quest_adventure.slay RPG gameplay demo with combat and save/load

================================================================================
                             ERROR MESSAGES
================================================================================

SlayScript uses themed error messages:

    Spell Miscast!          Syntax error
    Dark Magic Detected!    Lexer error (invalid characters)
    Unknown Incantation!    Undefined variable or function
    Forbidden Magic!        Type error
    Cursed Scroll!          Value error
    Prophecy Violation!     Tried to modify a constant
    Portal Failure!         Network error
    Voice Silenced!         Text-to-speech error
    Azure Realm Error!      Microsoft 365 / Entra ID error
    Scroll Damaged!         File I/O error
    Oracle Silent!          MySQL database error
    Quest Failed!           Gameplay mechanics error

================================================================================
                            PROJECT FILES
================================================================================

slayscript/
    __init__.py         Package initialization
    __main__.py         Entry point for python -m slayscript
    tokens.py           Token definitions
    lexer.py            Tokenizer
    ast_nodes.py        AST node classes
    parser.py           Recursive descent parser
    environment.py      Scope management
    interpreter.py      AST evaluator
    builtins.py         Built-in functions
    m365.py             Microsoft 365 / Entra ID functions
    errors.py           Exception classes
    main.py             CLI and REPL

build.bat               Windows build script (CMD)
build.ps1               Windows build script (PowerShell)
build.py                Cross-platform build script
slayscript_cli.py       Entry point for compiled executable
requirements.txt        Python dependencies
requirements-dev.txt    Development dependencies

================================================================================
                               LICENSE
================================================================================

SlayScript - Cast spells, slay bugs.

================================================================================
