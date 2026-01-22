================================================================================
                              SLAYSCRIPT
                        Cast spells, slay bugs.
================================================================================

A programming language inspired by Harry Potter and Buffy the Vampire Slayer,
featuring text-to-speech, networking, HTML/CSS generation, and enterprise
Microsoft 365 / Entra ID administration.

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
    - pyttsx3     Text-to-speech engine
    - msal        Microsoft Authentication Library (for M365)
    - requests    HTTP client (for M365)

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
