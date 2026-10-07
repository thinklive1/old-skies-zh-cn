##############################################################################
# Enemy class

init -2 python:
    class Enemy(store.object):
        def __init__(self, name, id, info, MAXHP, ATK, DEF, LUC, RES, EXP=0, G=0, drop=None, boss=False):
            self.name=name #enemy name as seen by the player
            self.id=id #string to be used as a codename
            self.info=info #enemy description

            #STATS
            self.MAXHP=MAXHP #base HP value
            self.ATK=ATK #physical attack points
            self.DEF=DEF #physical defense points
            self.LUC=LUC #factors into crit and dodge rate
            self.RES=RES #magic effectiveness multiplier

            #REWARDS (default to 0 or None)
            self.EXP=EXP #how much exp you get for defeating them
            self.G=G #gold earned by defeating them
            self.drop=drop #item to drop

            #extra
            self.boss=boss #if True, you can't run away

        # adds enemy to list of seen enemies
        def see_enemy(self):
            if self.id not in seen_enemies:
                seen_enemies.append(self.id)

# define your own enemies here!
define b_vai = Enemy(_("VAI5000"), "b_vai",
    info=_("輕快靈巧"),
    MAXHP=30, ATK=4, DEF=5, LUC=6, RES=.5,
    EXP=20, G=2)
define b_ruby = Enemy(_("RUBYRED"), "b_ruby",
    info=_("超級強勁的打擊"),
    MAXHP=40, ATK=10, DEF=7, LUC=1, RES=.5,
    EXP=20, G=2, drop="item_sucker")
define b_crusafix = Enemy(_("CRUSAFIX"), "b_crusafix",
    info=_("持久耐用"),
    MAXHP=75, ATK=9, DEF=12, LUC=2, RES=.5,
    EXP=20, G=2, drop="item_sucker")
define b_aftrr = Enemy(_("AFTRR"), "b_aftrr",
    info=_("全面均衡"),
    MAXHP=54, ATK=15, DEF=9, LUC=2, RES=.5,
    EXP=20, G=2)
define b_8tsukii = Enemy(_("8TSUKII"), "b_8tsukii",
    info=_("高抗性"),
    MAXHP=65, ATK=10, DEF=32, LUC=3, RES=.5,
    EXP=20, G=2)
define m_goop = Enemy(_("NUJIOH"), "m_goop",
    info=_("纖細男孩"),
    MAXHP=75, ATK=20, DEF=20, LUC=4, RES=.5,
    EXP=20, G=2, drop="item_sucker")
define b_swazy = Enemy(_("SWAZY*"), "b_swazy",
    info=_("正直無私"),
    MAXHP=90, ATK=25, DEF=32, LUC=3, RES=.5,
    EXP=20, G=2)
define b_oldman = Enemy(_("????"), "b_oldman",
    info=_("老前輩"),
    MAXHP=90, ATK=27, DEF=32, LUC=3, RES=.5,
    EXP=20, G=2)

##############################################################################
# Battle transforms
transform battle_party1:
    xalign .4
    yalign .52
transform battle_enemy1:
    xalign .6
    yalign .52

image battle bg = anim.Filmstrip("battlecore.png", (1280,720), (1,3), 0.4, loop=True)
image vaibattle bg = anim.Filmstrip("battlecore2.png", (1280,720), (1,3), 0.4, loop=True)
image crubattle bg = anim.Filmstrip("battlecore3.png", (1280,720), (1,3), 0.4, loop=True)
image tsubattle bg = anim.Filmstrip("battlecore4.png", (1280,720), (1,3), 0.4, loop=True)
image nujibattle bg = anim.Filmstrip("battlecore5.png", (1280,720), (1,3), 0.4, loop=True)
image swabattle bg = anim.Filmstrip("battlecore6.png", (1280,720), (1,3), 0.4, loop=True)
image oldmanbattle bg = anim.Filmstrip("battlecore8.png", (1280,720), (1,3), 0.4, loop=True)
image aftrrbattle bg = anim.Filmstrip("battlecore7.png", (1280,720), (1,3), 0.4, loop=True)
image stage bg = Frame("gui/frame2.png",4,4, xysize=(700,400), yoffset=-196)

##############################################################################
# Sprite animations

##PLAYER SPRITES
image player syrup idle:
    "player syrup idle1"

image player syrup attack:
    "player syrup attack1"

image player syrup hit:
    "player syrup hit1"
    pause .1
    "player syrup hit2"
    pause .06
    "player syrup hit1"
    pause .06
    "player syrup hit2"

image player syrup guard:
    "player syrup guard1"
image player syrup guardhit:
    "player syrup guard1"
image player syrup down:
    "player syrup down1"
    xoffset 10

image player syrup run:
    parallel:
        "player syrup run1"
        pause .1
        repeat
    parallel:
        xoffset 0
        easein .8 xoffset -150
    parallel:
        alpha 1.0
        pause .4
        linear .4 alpha 0

image player syrup win:
    "player syrup win1"
    pause .1
    block:
        "player syrup win2"
        pause .3
        "player syrup win1"
        pause .3
        repeat

##PLAYER anew SPRITES
image player anew idle:
    "player syrup idle1_a"

image player anew attack:
    "player syrup attack1_a"

image player anew hit:
    "player syrup hit1_a"
    pause .1
    "player syrup hit2_a"
    pause .06
    "player syrup hit1_a"
    pause .06
    "player syrup hit2_a"

image player anew guard:
    "player syrup guard1_a"
image player anew guardhit:
    "player syrup guard1_a"
image player anew down:
    "player syrup down1"
    xoffset 10

image player anew run:
    parallel:
        "player syrup run1"
        pause .1
        repeat
    parallel:
        xoffset 0
        easein .8 xoffset -150
    parallel:
        alpha 1.0
        pause .4
        linear .4 alpha 0

image player anew win:
    "player syrup win1_a"
    pause .1
    block:
        "player syrup win2_a"
        pause .3
        "player syrup win1_a"
        pause .3
        repeat

##ENEMY SPRITES
image enemy goop idle:
    "enemy goop idle1"
image enemy goop move:
    "enemy goop idle"
image enemy goop attack:
    "enemy goop idle"
    xoffset 0
    linear .06 xoffset -20
    easein .2 xoffset 0
image enemy goop dodge:
    "enemy goop idle"
    xoffset 0
    linear .06 xoffset 20
    easein .2 xoffset 0
image enemy goop hit:
    "enemy goop hit1"
    pause .1
    "enemy goop hit2"
    pause .06
    "enemy goop hit1"
    pause .06
    "enemy goop hit2"
image enemy goop down:
    "enemy goop down1"
    pause .1
    "enemy goop down2"
    pause 0.3
    "enemy goop down5"
    pause .1
    "enemy goop down6"

image enemy vai idle:
    "vai idle1"
image enemy vai move:
    "vai idle1"
image enemy vai attack:
    "vai idle1"
    xoffset 0
    linear .06 xoffset -20
    easein .2 xoffset 0
image enemy vai dodge:
    "vai idle1"
    xoffset 0
    linear .06 xoffset 20
    easein .2 xoffset 0
image enemy vai hit:
    "vai hit1"
    pause .1
    "vai hit2"
    pause .06
    "vai hit1"
    pause .06
    "vai hit2"
image enemy vai down:
    "vai down1"


image enemy oldman idle:
    "oldman idle1"
image enemy oldman move:
    "oldman idle1"
image enemy oldman attack:
    "oldman idle1"
    xoffset 0
    linear .06 xoffset -20
    easein .2 xoffset 0
image enemy oldman dodge:
    "oldman idle1"
    xoffset 0
    linear .06 xoffset 20
    easein .2 xoffset 0
image enemy oldman hit:
    "oldman hit1"
    pause .1
    "oldman hit2"
    pause .06
    "oldman hit1"
    pause .06
    "oldman hit2"
image enemy oldman down:
    "oldman down1"

image enemy ruby idle:
    "ruby idle1"
image enemy ruby move:
    "ruby idle1"
image enemy ruby attack:
    "ruby idle1"
    xoffset 0
    linear .06 xoffset -20
    easein .2 xoffset 0
image enemy ruby dodge:
    "ruby idle1"
    xoffset 0
    linear .06 xoffset 20
    easein .2 xoffset 0
image enemy ruby hit:
    "ruby hit1"
    pause .1
    "ruby hit2"
    pause .06
    "ruby hit1"
    pause .06
    "ruby hit2"
image enemy ruby down:
    "ruby down1"



image enemy crusafix idle:
    "crusafix idle1"
image enemy crusafix move:
    "crusafix idle1"
image enemy crusafix attack:
    "crusafix idle1"
    xoffset 0
    linear .06 xoffset -20
    easein .2 xoffset 0
image enemy crusafix dodge:
    "crusafix idle1"
    xoffset 0
    linear .06 xoffset 20
    easein .2 xoffset 0
image enemy crusafix hit:
    "crusafix hit1"
    pause .1
    "crusafix hit2"
    pause .06
    "crusafix hit1"
    pause .06
    "crusafix hit2"
image enemy crusafix down:
    "crusafix down1"


image enemy aftrr idle:
    "aftrr idle1"
image enemy aftrr move:
    "aftrr idle1"
image enemy aftrr attack:
    "aftrr idle1"
    xoffset 0
    linear .06 xoffset -20
    easein .2 xoffset 0
image enemy aftrr dodge:
    "aftrr idle1"
    xoffset 0
    linear .06 xoffset 20
    easein .2 xoffset 0
image enemy aftrr hit:
    "aftrr hit1"
    pause .1
    "aftrr hit2"
    pause .06
    "aftrr hit1"
    pause .06
    "aftrr hit2"
image enemy aftrr down:
    "aftrr down1"

image enemy tsukii idle:
    "aftrr2 idle1"
image enemy tsukii move:
    "aftrr2 idle1"
image enemy tsukii attack:
    "aftrr2 idle1"
    xoffset 0
    linear .06 xoffset -20
    easein .2 xoffset 0
image enemy tsukii dodge:
    "aftrr2 idle1"
    xoffset 0
    linear .06 xoffset 20
    easein .2 xoffset 0
image enemy tsukii hit:
    "tsukii hit1"
    pause .1
    "tsukii hit2"
    pause .06
    "tsukii hit1"
    pause .06
    "tsukii hit2"
image enemy tsukii down:
    "tsukii down1"

image enemy swazy idle:
    "aftrr3 idle1"
image enemy swazy move:
    "aftrr3 idle1"
image enemy swazy attack:
    "aftrr3 idle1"
    xoffset 0
    linear .06 xoffset -20
    easein .2 xoffset 0
image enemy swazy dodge:
    "aftrr3 idle1"
    xoffset 0
    linear .06 xoffset 20
    easein .2 xoffset 0
image enemy swazy hit:
    "swazy hit1"
    pause .1
    "swazy hit2"
    pause .06
    "swazy hit1"
    pause .06
    "swazy hit2"
image enemy swazy down:
    "swazy down1"
