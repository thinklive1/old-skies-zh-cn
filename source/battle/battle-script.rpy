##############################################################################
## BATTLE SYSTEM!!!!!!
# don't allow mid-battle saves, it might mess things up...

# battle text is a special character
define bt = Character(None, window_background="gui/textbox.png", what_font="unif.otf") #you can replace the textbox image, font, whatever else
define bt2 = Character(None, window_background="gui/anewbox.png", what_font="unif.otf")
# add these in if you want: #what_font="", what_size=, what_color=""

# player stat values are set by a list so it can check the corresponding stat to what level you are
define HPvalues = [0, 30,34,42,48,50, 54,58,62,68,70]
define ATKvalues = [0, 5,6,8,9,12, 15,19,23,27,32]
define DEFvalues = [0, 3,4,5,7,9, 12,14,17,20,23]
define LUCvalues = [0, 1,2,4,6,7, 9,10,12,13,15]


label vai_battle:

    ## put this block at the beginning of your start label
    $ persistent.inbattlevai = True
    python:
        # disable rollback during battle
        battling = False
        renpy.suspend_rollback(battling)

        # battle stats
        playerLV = 1
        playerMAXHP = HPvalues[1]
        playerHP = HPvalues[1]
        playerATK = ATKvalues[2]
        playerDEF = DEFvalues[2]
        playerLUC = LUCvalues[1]
        playerEXP = 0

        # calculate exp to next level
        nextEXP = round( 0.04 * (playerLV ** 3) + 0.8 * (playerLV ** 2) + 2 * playerLV)
        # this formula is from disgaea, apparently!
        # http://howtomakeanrpg.com/a/how-to-make-an-rpg-levels.html

        # enemy defaults
        enemyHP = 1
        seen_enemies = []
    ##

    # put the rest of this in script.rpy wherever you want the enter a battle

    scene vaibattle bg # fullscreen background
    show stage bg # frame the characters stand inside (feel free to remove)

    # set the enemy to fight
    $ enemy = b_vai

    # and show their sprite!
    show enemy vai idle at battle_enemy1, zoomx(3)

    call battle_start from _call_battle_start

    # return ot the main game loop
    jump battle_vai_exit

label ruby_battle:

    ## put this block at the beginning of your start label
    $ persistent.inbattleruby = True
    python:
        # disable rollback during battle
        battling = False
        renpy.suspend_rollback(battling)

        # battle stats
        if persistent.vaiwon != True:
            playerLV = 1
            playerMAXHP = HPvalues[1]
            playerHP = HPvalues[1]
            playerATK = ATKvalues[2]
            playerDEF = DEFvalues[2]
            playerLUC = LUCvalues[1]
            playerEXP = 0
        else:
            playerLV = 2
            playerMAXHP = HPvalues[3]
            playerHP = HPvalues[3]
            playerATK = ATKvalues[4]
            playerDEF = DEFvalues[3]
            playerLUC = LUCvalues[1]
            playerEXP = 0

        # calculate exp to next level
        nextEXP = round( 0.04 * (playerLV ** 3) + 0.8 * (playerLV ** 2) + 2 * playerLV)
        # this formula is from disgaea, apparently!
        # http://howtomakeanrpg.com/a/how-to-make-an-rpg-levels.html

        # enemy defaults
        enemyHP = 1
        seen_enemies = []
    ##

    # put the rest of this in script.rpy wherever you want the enter a battle

    scene battle bg # fullscreen background
    show stage bg # frame the characters stand inside (feel free to remove)

    # set the enemy to fight
    $ enemy = b_ruby

    # and show their sprite!
    show enemy ruby idle at battle_enemy1, zoomx(3)

    call battle_start from _call_battle_start_1

    # return ot the main game loop
    jump battle_ruby_exit

label crusafix_battle:

    ## put this block at the beginning of your start label
    $ persistent.inbattlecrusafix = True
    python:
        # disable rollback during battle
        battling = False
        renpy.suspend_rollback(battling)

        # battle stats
        if persistent.vaiwon != True:
            playerLV = 1
            playerMAXHP = HPvalues[1]
            playerHP = HPvalues[1]
            playerATK = ATKvalues[2]
            playerDEF = DEFvalues[2]
            playerLUC = LUCvalues[1]
            playerEXP = 0
        elif persistent.rubywon != True:
            playerLV = 2
            playerMAXHP = HPvalues[3]
            playerHP = HPvalues[3]
            playerATK = ATKvalues[4]
            playerDEF = DEFvalues[3]
            playerLUC = LUCvalues[1]
            playerEXP = 0
        else:
            playerLV = 3
            playerMAXHP = HPvalues[5]
            playerHP = HPvalues[5]
            playerATK = ATKvalues[5]
            playerDEF = DEFvalues[4]
            playerLUC = LUCvalues[2]
            playerEXP = 0

        # calculate exp to next level
        nextEXP = round( 0.04 * (playerLV ** 3) + 0.8 * (playerLV ** 2) + 2 * playerLV)
        # this formula is from disgaea, apparently!
        # http://howtomakeanrpg.com/a/how-to-make-an-rpg-levels.html

        # enemy defaults
        enemyHP = 1
        seen_enemies = []
    ##

    # put the rest of this in script.rpy wherever you want the enter a battle

    scene crubattle bg # fullscreen background
    show stage bg # frame the characters stand inside (feel free to remove)

    # set the enemy to fight
    $ enemy = b_crusafix

    # and show their sprite!
    show enemy crusafix idle at battle_enemy1, zoomx(3)

    call battle_start from _call_battle_start_2

    # return ot the main game loop
    jump battle_crusafix_exit

label aftrr_battle:

    ## put this block at the beginning of your start label
    $ persistent.inbattleaftrr = True
    python:
        # disable rollback during battle
        battling = False
        renpy.suspend_rollback(battling)

        # battle stats
        if persistent.vaiwon != True:
            playerLV = 1
            playerMAXHP = HPvalues[1]
            playerHP = HPvalues[1]
            playerATK = ATKvalues[2]
            playerDEF = DEFvalues[2]
            playerLUC = LUCvalues[1]
            playerEXP = 0
        elif persistent.rubywon != True:
            playerLV = 2
            playerMAXHP = HPvalues[3]
            playerHP = HPvalues[3]
            playerATK = ATKvalues[4]
            playerDEF = DEFvalues[3]
            playerLUC = LUCvalues[1]
            playerEXP = 0
        elif persistent.crusafixwon != True:
            playerLV = 3
            playerMAXHP = HPvalues[5]
            playerHP = HPvalues[5]
            playerATK = ATKvalues[5]
            playerDEF = DEFvalues[4]
            playerLUC = LUCvalues[2]
            playerEXP = 0
        else:
            playerLV = 4
            playerMAXHP = HPvalues[6]
            playerHP = HPvalues[5]
            playerATK = ATKvalues[6]
            playerDEF = DEFvalues[5]
            playerLUC = LUCvalues[2]
            playerEXP = 0

        # calculate exp to next level
        nextEXP = round( 0.04 * (playerLV ** 3) + 0.8 * (playerLV ** 2) + 2 * playerLV)
        # this formula is from disgaea, apparently!
        # http://howtomakeanrpg.com/a/how-to-make-an-rpg-levels.html

        # enemy defaults
        enemyHP = 1
        seen_enemies = []
    ##

    # put the rest of this in script.rpy wherever you want the enter a battle

    scene aftrrbattle bg # fullscreen background
    show stage bg # frame the characters stand inside (feel free to remove)

    # set the enemy to fight
    $ enemy = b_aftrr

    # and show their sprite!
    show enemy aftrr idle at battle_enemy1, zoomx(3)

    call battle_start from _call_battle_start_3

    # return ot the main game loop
    jump battle_aftrr_exit

label tsukii_battle:

    ## put this block at the beginning of your start label
    $ persistent.inbattle8tsukii = True
    python:
        # disable rollback during battle
        battling = False
        renpy.suspend_rollback(battling)

        # battle stats
        if persistent.vaiwon != True:
            playerLV = 1
            playerMAXHP = HPvalues[1]
            playerHP = HPvalues[1]
            playerATK = ATKvalues[2]
            playerDEF = DEFvalues[2]
            playerLUC = LUCvalues[1]
            playerEXP = 0
        elif persistent.rubywon != True:
            playerLV = 2
            playerMAXHP = HPvalues[3]
            playerHP = HPvalues[3]
            playerATK = ATKvalues[4]
            playerDEF = DEFvalues[3]
            playerLUC = LUCvalues[1]
            playerEXP = 0
        elif persistent.crusafixwon != True:
            playerLV = 3
            playerMAXHP = HPvalues[5]
            playerHP = HPvalues[5]
            playerATK = ATKvalues[5]
            playerDEF = DEFvalues[4]
            playerLUC = LUCvalues[2]
            playerEXP = 0
        elif persistent.aftrrwon != True:
            playerLV = 4
            playerMAXHP = HPvalues[6]
            playerHP = HPvalues[5]
            playerATK = ATKvalues[6]
            playerDEF = DEFvalues[5]
            playerLUC = LUCvalues[2]
            playerEXP = 0
        else:
            playerLV = 5
            playerMAXHP = HPvalues[8]
            playerHP = HPvalues[8]
            playerATK = ATKvalues[7]
            playerDEF = DEFvalues[7]
            playerLUC = LUCvalues[3]
            playerEXP = 0

        # calculate exp to next level
        nextEXP = round( 0.04 * (playerLV ** 3) + 0.8 * (playerLV ** 2) + 2 * playerLV)
        # this formula is from disgaea, apparently!
        # http://howtomakeanrpg.com/a/how-to-make-an-rpg-levels.html

        # enemy defaults
        enemyHP = 1
        seen_enemies = []
    ##

    # put the rest of this in script.rpy wherever you want the enter a battle

    scene tsubattle bg # fullscreen background
    show stage bg # frame the characters stand inside (feel free to remove)

    # set the enemy to fight
    $ enemy = b_8tsukii

    # and show their sprite!
    show enemy tsukii idle at battle_enemy1, zoomx(3)

    call battle_start from _call_battle_start_4

    # return ot the main game loop
    jump battle_8tsukii_exit

label nuji_battle:

    ## put this block at the beginning of your start label
    $ persistent.inbattlenujioh = True
    python:
        # disable rollback during battle
        battling = False
        renpy.suspend_rollback(battling)

        # battle stats
        if persistent.vaiwon != True:
            playerLV = 1
            playerMAXHP = HPvalues[1]
            playerHP = HPvalues[1]
            playerATK = ATKvalues[2]
            playerDEF = DEFvalues[2]
            playerLUC = LUCvalues[1]
            playerEXP = 0
        elif persistent.rubywon != True:
            playerLV = 2
            playerMAXHP = HPvalues[3]
            playerHP = HPvalues[3]
            playerATK = ATKvalues[4]
            playerDEF = DEFvalues[3]
            playerLUC = LUCvalues[1]
            playerEXP = 0
        elif persistent.crusafixwon != True:
            playerLV = 3
            playerMAXHP = HPvalues[5]
            playerHP = HPvalues[5]
            playerATK = ATKvalues[5]
            playerDEF = DEFvalues[4]
            playerLUC = LUCvalues[2]
            playerEXP = 0
        elif persistent.aftrrwon != True:
            playerLV = 4
            playerMAXHP = HPvalues[6]
            playerHP = HPvalues[5]
            playerATK = ATKvalues[6]
            playerDEF = DEFvalues[5]
            playerLUC = LUCvalues[2]
            playerEXP = 0
        elif persistent.tsukiiwon != True:
            playerLV = 5
            playerMAXHP = HPvalues[8]
            playerHP = HPvalues[8]
            playerATK = ATKvalues[7]
            playerDEF = DEFvalues[7]
            playerLUC = LUCvalues[3]
            playerEXP = 0
        else:
            playerLV = 6
            playerMAXHP = HPvalues[9]
            playerHP = HPvalues[9]
            playerATK = ATKvalues[7]
            playerDEF = DEFvalues[8]
            playerLUC = LUCvalues[3]
            playerEXP = 0

        # calculate exp to next level
        nextEXP = round( 0.04 * (playerLV ** 3) + 0.8 * (playerLV ** 2) + 2 * playerLV)
        # this formula is from disgaea, apparently!
        # http://howtomakeanrpg.com/a/how-to-make-an-rpg-levels.html

        # enemy defaults
        enemyHP = 1
        seen_enemies = []
    ##

    # put the rest of this in script.rpy wherever you want the enter a battle

    scene nujibattle bg # fullscreen background
    show stage bg # frame the characters stand inside (feel free to remove)

    # set the enemy to fight
    $ enemy = m_goop

    # and show their sprite!
    show enemy goop idle at battle_enemy1, zoomx(3)

    call battle_start from _call_battle_start_5

    # return ot the main game loop
    jump battle_nuji_exit

label swazy_battle:

    ## put this block at the beginning of your start label
    $ persistent.inbattleswazy = True
    python:
        # disable rollback during battle
        battling = False
        renpy.suspend_rollback(battling)

        # battle stats
        if persistent.vaiwon != True:
            playerLV = 1
            playerMAXHP = HPvalues[1]
            playerHP = HPvalues[1]
            playerATK = ATKvalues[2]
            playerDEF = DEFvalues[2]
            playerLUC = LUCvalues[1]
            playerEXP = 0
        elif persistent.rubywon != True:
            playerLV = 2
            playerMAXHP = HPvalues[3]
            playerHP = HPvalues[3]
            playerATK = ATKvalues[4]
            playerDEF = DEFvalues[3]
            playerLUC = LUCvalues[1]
            playerEXP = 0
        elif persistent.crusafixwon != True:
            playerLV = 3
            playerMAXHP = HPvalues[5]
            playerHP = HPvalues[5]
            playerATK = ATKvalues[5]
            playerDEF = DEFvalues[4]
            playerLUC = LUCvalues[2]
            playerEXP = 0
        elif persistent.aftrrwon != True:
            playerLV = 4
            playerMAXHP = HPvalues[6]
            playerHP = HPvalues[5]
            playerATK = ATKvalues[6]
            playerDEF = DEFvalues[5]
            playerLUC = LUCvalues[2]
            playerEXP = 0
        elif persistent.tsukiiwon != True:
            playerLV = 5
            playerMAXHP = HPvalues[8]
            playerHP = HPvalues[8]
            playerATK = ATKvalues[7]
            playerDEF = DEFvalues[7]
            playerLUC = LUCvalues[3]
            playerEXP = 0
        elif persistent.nujiohwon != True:
            playerLV = 6
            playerMAXHP = HPvalues[9]
            playerHP = HPvalues[9]
            playerATK = ATKvalues[7]
            playerDEF = DEFvalues[8]
            playerLUC = LUCvalues[3]
            playerEXP = 0
        else:
            playerLV = 7
            playerMAXHP = HPvalues[10]
            playerHP = HPvalues[10]
            playerATK = ATKvalues[8]
            playerDEF = DEFvalues[9]
            playerLUC = LUCvalues[3]
            playerEXP = 0

        # calculate exp to next level
        nextEXP = round( 0.04 * (playerLV ** 3) + 0.8 * (playerLV ** 2) + 2 * playerLV)
        # this formula is from disgaea, apparently!
        # http://howtomakeanrpg.com/a/how-to-make-an-rpg-levels.html

        # enemy defaults
        enemyHP = 1
        seen_enemies = []
    ##

    # put the rest of this in script.rpy wherever you want the enter a battle

    scene swabattle bg # fullscreen background
    show stage bg # frame the characters stand inside (feel free to remove)

    # set the enemy to fight
    $ enemy = b_swazy

    # and show their sprite!
    show enemy swazy idle at battle_enemy1, zoomx(3)

    call battle_start from _call_battle_start_6

    # return ot the main game loop
    jump battle_swazy_exit

label oldman_battle:

    ## put this block at the beginning of your start label
    $ persistent.inbattleoldman = True
    python:
        # disable rollback during battle
        battling = False
        renpy.suspend_rollback(battling)

        # battle stats
        if persistent.fixcheck != True:
            playerLV = 1
            playerMAXHP = HPvalues[1]
            playerHP = HPvalues[1]
            playerATK = ATKvalues[2]
            playerDEF = DEFvalues[2]
            playerLUC = LUCvalues[1]
            playerEXP = 0
        else:
            playerLV = 7
            playerMAXHP = HPvalues[10]
            playerHP = HPvalues[10]
            playerATK = ATKvalues[8]
            playerDEF = DEFvalues[9]
            playerLUC = LUCvalues[3]
            playerEXP = 0

        # calculate exp to next level
        nextEXP = round( 0.04 * (playerLV ** 3) + 0.8 * (playerLV ** 2) + 2 * playerLV)
        # this formula is from disgaea, apparently!
        # http://howtomakeanrpg.com/a/how-to-make-an-rpg-levels.html

        # enemy defaults
        enemyHP = 1
        seen_enemies = []
    ##

    # put the rest of this in script.rpy wherever you want the enter a battle

    scene oldmanbattle bg # fullscreen background
    show stage bg # frame the characters stand inside (feel free to remove)

    # set the enemy to fight
    $ enemy = b_oldman

    # and show their sprite!
    show enemy oldman idle at battle_enemy1, zoomx(3)

    call battle_startx from _call_battle_start_7

    # return ot the main game loop
    jump battle_oldman_exit

label battle_startx:

    #SETUP TIME
    python:
        _game_menu_screen = None
        _history = False
        quick_menu = False

        battling = True
        turn = 0
        battle_events = [] # tracks one-time conditional lines

        atkbuff = 0
        defbuff = 0
        CRIT = False
        consecutive_miss = 0

        enemy.see_enemy()
        enemyHP = enemy.MAXHP

    if persistent.anewbattle != True:
        show player syrup idle at battle_party1, zoomx(3) behind enemy
    if persistent.anewbattle == True:
        show player anew idle at battle_party1, zoomx(3) behind enemy

    if persistent.anewbattle != True:
        bt "它是： [enemy.name!t]."
    if persistent.anewbattle == True:
        bt2 "它是： [enemy.name!t]."

    show screen battleoverlay


label battle_start:

    #SETUP TIME
    python:
        _game_menu_screen = None
        _history = False
        quick_menu = False

        battling = True
        turn = 0
        battle_events = [] # tracks one-time conditional lines

        atkbuff = 0
        defbuff = 0
        CRIT = False
        consecutive_miss = 0

        enemy.see_enemy()
        enemyHP = enemy.MAXHP

    if persistent.anewbattle != True:
        show player syrup idle at battle_party1, zoomx(3) behind enemy
    if persistent.anewbattle == True:
        show player anew idle at battle_party1, zoomx(3) behind enemy

    if persistent.anewbattle != True:
        bt "它是： [enemy.name!t]."
    if persistent.anewbattle == True:
        bt2 "它是：[enemy.name!t]."


    show screen battleoverlay

##############################################################################
## PLAYER TURN

label battle_turn:
    # start of player turn
    $ turn += 1
    $ guard = False

    call screen battle_menu

label battle_attack:
    # damage calculation
    $ damage = playerATK*4 + atkbuff - enemy.DEF*2
    if persistent.anewbattle != True:
        bt "你攻擊"
    if persistent.anewbattle == True:
        bt2 "你攻擊"

    show player attack

    # roll for crits/misses
    $ d6roll = renpy.random.randint(1, 6)

    # no chance of miss if enemy has lower luck
    if enemy.LUC>playerLUC:
        if d6roll < 4 and consecutive_miss < 2: # never miss 3 times in a row
            jump battle_miss

    # reaching this line means you didn't miss, so reset the counter
    $ consecutive_miss = 0

    # 1 in 6 chance of critical hit
    if d6roll==3:
        $ CRIT = True
        $ damage = int(damage*1.5)

    jump battle_damage

label battle_miss:
    show screen showmiss
    show enemy dodge
    play sound "fx/hit.mp3"
    if persistent.anewbattle != True:
        bt "[enemy.name!t]躲開了攻擊"
    if persistent.anewbattle == True:
        bt2 "[enemy.name!t]躲開了攻擊"
    $ consecutive_miss += 1
    jump battle_attack_result

label battle_damage:

    # can't deal negative damage
    if damage < 0:
        $ damage = 0
    $ enemyHP -= damage
    # enemy can't have negative hp
    if enemyHP < 0:
        $ enemyHP = 0

    if CRIT:
        show screen showcrit
    else:
        show screen showdamage("enemy")

    show enemy hit
    if CRIT:
        play sound "fx/stars.mp3"
        if persistent.anewbattle != True:
            bt "強勁一擊" with vpunch
        if persistent.anewbattle == True:
            bt2 "強勁一擊" with vpunch

    else:
        play sound "fx/ah.mp3"
        if persistent.anewbattle != True:
            bt "擊中!"
        if persistent.anewbattle == True:
            bt2 "擊中!"
    $ CRIT= False

label battle_attack_result:

    if enemyHP <= 0:
        jump battle_won

    show player idle
    show enemy idle

    jump battle_enemy_turn

label battle_defend:
    $ guard = True
    show player guard
    if persistent.anewbattle != True:
        bt "你正在捍衛"
    if persistent.anewbattle == True:
        bt2 "你正在捍衛"
    jump battle_enemy_turn

label use_sucker:
    $ inv.remove("item_sucker")
    $ damage = int(playerMAXHP/2)
    $ playerHP += damage
    show screen showheal
    if playerHP > playerMAXHP:
        $ playerHP = playerMAXHP
    if persistent.anewbattle != True:
        bt "{color=#007dff}已使用藥水{/color}!"
    if persistent.anewbattle == True:
        bt2 "{color=#007dff}已使用藥水{/color}!"
    jump battle_enemy_turn

##############################################################################
## ENEMY TURN

label battle_enemy_turn:

    if persistent.anewbattle != True:
        bt "[enemy.name!t] 攻擊"
    if persistent.anewbattle == True:
        bt2 "[enemy.name!t] 攻擊"
    show enemy attack

label battle_enemy_damage:
    $ randomdamage = renpy.random.randint(1, 10)
    if persistent.inbattleaftrr == True and persistent.crusafixwon != True:
        $ damage = (enemy.ATK*9999 - playerDEF*2 - defbuff)
    elif persistent.inbattle8tsukii == True and persistent.aftrrwon != True:
        $ damage = (enemy.ATK*9999 - playerDEF*2 - defbuff)
    elif persistent.inbattlenujioh == True and persistent.tsukiiwon != True:
        $ damage = (enemy.ATK*9999 - playerDEF*2 - defbuff)
    elif persistent.inbattleswazy == True and persistent.nujiohwon != True:
        $ damage = (enemy.ATK*9999 - playerDEF*2 - defbuff)
    elif randomdamage == 1:
        $ randomdamage = renpy.random.randint(1, 10)
        if persistent.inbattleswazy == True:
            $ damage = (enemy.ATK*10 - playerDEF*2 - defbuff)
        elif persistent.inbattleoldman == True:
            $ damage = (enemy.ATK*10 - playerDEF*2 - defbuff)
        else:
            $ damage = (enemy.ATK*5 - playerDEF*2 - defbuff)
    elif randomdamage == 3:
        $ randomdamage = renpy.random.randint(1, 10)
        if persistent.inbattleswazy == True:
            $ damage = (enemy.ATK*0.1 - playerDEF*2 - defbuff)
        elif persistent.inbattleoldman == True:
            $ damage = (enemy.ATK*0.1 - playerDEF*2 - defbuff)
        else:
            $ damage = (enemy.ATK*3 - playerDEF*2 - defbuff)
    elif randomdamage == 4:
        $ randomdamage = renpy.random.randint(1, 10)
        if persistent.inbattleswazy == True:
            $ damage = (enemy.ATK*2 - playerDEF*2 - defbuff)
        elif persistent.inbattleoldman == True:
            $ damage = (enemy.ATK*2 - playerDEF*2 - defbuff)
        else:
            $ damage = (enemy.ATK*3 - playerDEF*2 - defbuff)
    elif randomdamage == 5 and persistent.inbattleswazy == True:
        $ randomdamage = renpy.random.randint(1, 10)
        $ damage = (enemy.ATK*2 - playerDEF*2 - defbuff)
    elif randomdamage == 6 and persistent.inbattleswazy == True:
        $ randomdamage = renpy.random.randint(1, 10)
        $ damage = (enemy.ATK*5 - playerDEF*2 - defbuff)
    elif randomdamage == 7 and persistent.inbattleswazy == True:
        $ randomdamage = renpy.random.randint(1, 10)
        $ damage = (enemy.ATK*3 - playerDEF*2 - defbuff)
    elif randomdamage == 8 and persistent.inbattleswazy == True:
        $ randomdamage = renpy.random.randint(1, 10)
        $ damage = (enemy.ATK*2 - playerDEF*2 - defbuff)
    elif randomdamage == 9 and persistent.inbattleswazy == True:
        $ randomdamage = renpy.random.randint(1, 10)
        $ damage = (enemy.ATK*2 - playerDEF*2 - defbuff)

    elif randomdamage == 5 and persistent.inbattleoldman == True:
        $ randomdamage = renpy.random.randint(1, 10)
        $ damage = (enemy.ATK*2 - playerDEF*2 - defbuff)
    elif randomdamage == 6 and persistent.inbattleoldman == True:
        $ randomdamage = renpy.random.randint(1, 10)
        $ damage = (enemy.ATK*5 - playerDEF*2 - defbuff)
    elif randomdamage == 7 and persistent.inbattleoldman == True:
        $ randomdamage = renpy.random.randint(1, 10)
        $ damage = (enemy.ATK*3 - playerDEF*2 - defbuff)
    elif randomdamage == 8 and persistent.inbattleoldman == True:
        $ randomdamage = renpy.random.randint(1, 10)
        $ damage = (enemy.ATK*2 - playerDEF*2 - defbuff)
    elif randomdamage == 9 and persistent.inbattleoldman == True:
        $ randomdamage = renpy.random.randint(1, 10)
        $ damage = (enemy.ATK*2 - playerDEF*2 - defbuff)

    else:
        $ damage = (enemy.ATK*4 - playerDEF*2 - defbuff)

    if guard: #halve damage
        $ damage = int(damage/2)

    if damage <= 0: #can't do negative damage
    #always take at least 1 damage unless you guard
        if guard:
            $ damage = 0
        else:
            $ damage = 1

    # now apply to syrup...
    $ playerHP -= damage

    if playerHP<=0:
        $ playerHP = 0

    show screen showdamage("player")

    if guard and playerHP > 0:
        show player guardhit
    else:
        show player hit

    # different text for different damage results
    if guard and playerHP > 0:
        if damage>0 and playerHP != playerMAXHP:
            play sound "fx/in.mp3"
            if persistent.anewbattle != True:
                bt "你成功抵禦了攻擊"
                bt "部分生命值已恢復"
            if persistent.anewbattle == True:
                bt2 "你成功抵禦了攻擊"
                bt2 "部分生命值已恢復"
            $ playerHP += damage
            $ randomdef = renpy.random.randint(1, 10)
            if randomdef == 1:
                if persistent.anewbattle != True:
                    bt "攻擊突破了你的防禦"
                if persistent.anewbattle == True:
                    bt2 "攻擊突破了你的防禦E"
                $ playerHP -= 10
            elif randomdef == 3:
                $ playerHP += 1
            elif randomdef == 4:
                $ playerHP += 1
            elif randomdef == 5:
                $ playerHP += 1
            elif randomdef == 6:
                $ playerHP += 1
            elif randomdef == 7:
                $ playerHP += 0
            elif randomdef == 8:
                $ playerHP += 0
            elif randomdef == 9:
                $ playerHP += 10
            elif randomdef == 10:
                if persistent.anewbattle != True:
                    bt "攻擊突破了你的防禦"
                if persistent.anewbattle == True:
                    bt2 "攻擊突破了你的防禦"
                $ playerHP -= 15
            else:
                $ playerHP -= 1

        elif damage>0:
            play sound "fx/in.mp3"
            if persistent.anewbattle != True:
                bt "你成功抵禦了攻擊"
            if persistent.anewbattle == True:
                bt2 "你成功抵禦了攻擊"
            $ playerHP += damage
            $ playerHP -= 1
        else:
            play sound "fx/in.mp3"
            if persistent.anewbattle != True:
                bt "完美擋下！"
            if persistent.anewbattle == True:
                bt2 "完美擋下！"
    else:
        play sound "fx/ah.mp3"
        if persistent.anewbattle != True:
            bt "你受到傷害"
        if persistent.anewbattle == True:
            bt2 "你受到傷害"

label battle_enemy_turn_end:
    show player idle
    show enemy idle
# you lose when your HP runs out
    if playerHP <= 0:
        jump battle_lost
# if you hit 25% health, warn the player
    if playerHP <= playerMAXHP/4:
        if "lowHP" not in battle_events:
            jump battle_lowhp

    jump battle_turn

label battle_lowhp:
    if persistent.anewbattle != True:
        bt "你快死了。"
    if persistent.anewbattle == True:
        bt2 "你快死了。"
    $ battle_events.append("lowHP")
    jump battle_turn

##############################################################################
## OUTCOME

label battle_ran:
    hide screen battleoverlay

    show player run
    bt "ESCAPE!"
    jump battle_end

label battle_lost:
    hide screen battleoverlay

    show player down
    if persistent.anewbattle != True:
        bt "敗北..."
    if persistent.anewbattle == True:
        bt2 "敗北..."
    jump battle_end

label battle_won:
    hide screen battleoverlay

    show player win
    show enemy down
    play sound "fx/inp.mp3"
    if persistent.anewbattle != True:
        bt "你贏了！"
    if persistent.anewbattle == True:
        bt2 "你贏了！"

    if persistent.inbattlevai == True:
        $ persistent.vaiwon = True
    if persistent.inbattleruby == True:
        $ persistent.rubywon = True
    if persistent.inbattlecrusafix == True:
        $ persistent.crusafixwon = True
    if persistent.inbattleaftrr == True:
        $ persistent.aftrrwon = True
    if persistent.inbattle8tsukii == True:
        $ persistent.tsukiiwon = True
    if persistent.inbattlenujioh == True:
        $ persistent.nujiohwon = True
    if persistent.inbattleswazy == True:
        $ persistent.swazywon = True
    if persistent.inbattleoldman == True:
        $ persistent.oldmanwon = True
    # gain exp and possibly level up
    if not playerLV==100: # level cap
        $ playerEXP += enemy.EXP
        #bt "YOU GAIN [enemy.EXP] EXP"
        #if playerEXP >= int(nextEXP):
            #call levelup

    if enemy.drop:
        call battle_drops from _call_battle_drops

    jump battle_end

label levelup:

    if playerEXP >= int(nextEXP) and not playerLV==10:
        $ playerLV += 1
        # calculate amount of xp needed at your current level
        $ nextEXP = round( 0.04 * (playerLV ** 3) + 0.8 * (playerLV ** 2) + 2 * playerLV)
        #loop here in case you get enough xp to level twice
        jump levelup

    bt "YOU ARE NOW LEVEL [playerLV]!"
    # increase stats
    $ playerMAXHP = HPvalues[playerLV]
    $ playerATK = ATKvalues[playerLV]
    $ playerDEF = DEFvalues[playerLV]
    $ playerLUC = LUCvalues[playerLV]

    return

label battle_drops:

    $ newitem = InvItem(*set_item(enemy.drop))
    show screen reward(newitem.image)
    $ newitem.pickup()

    bt "[enemy.name!t] 給予 \n{color=#007dff}[newitem.name!t]{/color}!"

    hide screen reward

    return

label battle_end:
    # return the game to its normal state
    python:
        _game_menu_screen = "save"
        _history = True
        quick_menu = True

        battling = False
    # jump back to where you called battle_start
    return
