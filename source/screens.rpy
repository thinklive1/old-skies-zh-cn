################################################################################
## Initialization
################################################################################

init offset = -1


################################################################################
## Styles
################################################################################

style default:
    properties gui.text_properties()
    language gui.language

style input:
    properties gui.text_properties("input", accent=True)
    adjust_spacing False

style hyperlink_text:
    properties gui.text_properties("hyperlink", accent=True)
    hover_underline True

style gui_text:
    properties gui.text_properties("interface")


style button:
    properties gui.button_properties("button")

style button_text is gui_text:
    properties gui.text_properties("button")
    yalign 0.5


style label_text is gui_text:
    properties gui.text_properties("label", accent=True)

style prompt_text is gui_text:
    properties gui.text_properties("prompt")


style bar:
    ysize gui.bar_size
    left_bar Frame("gui/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    xsize gui.bar_size
    top_bar Frame("gui/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    ysize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    xsize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    ysize gui.slider_size
    base_bar Frame("gui/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/slider/horizontal_[prefix_]thumb.png"

style vslider:
    xsize gui.slider_size
    base_bar Frame("gui/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/slider/vertical_[prefix_]thumb.png"


style frame:
    padding gui.frame_borders.padding
    background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)



################################################################################
## In-game screens
################################################################################


## Say screen ##################################################################
##
## The say screen is used to display dialogue to the player. It takes two
## parameters, who and what, which are the name of the speaking character and
## the text to be displayed, respectively. (The who parameter can be None if no
## name is given.)
##
## This screen must create a text displayable with id "what", as Ren'Py uses
## this to manage text display. It can also create displayables with id "who"
## and id "window" to apply style properties.
##
## https://www.renpy.org/doc/html/screen_special.html#say

screen say(who, what):
    style_prefix "say"

    window:
        id "window"

        if who is not None:

            window:
                id "namebox"
                style "namebox"
                text who id "who"

        text what id "what"


    ## If there's a side image, display it above the text. Do not display on the
    ## phone variant - there's no room.
    if not renpy.variant("small"):
        add SideImage() xalign 0.0 yalign 1.0



## Make the namebox available for styling through the Character object.
init python:
    config.character_id_prefixes.append('namebox')

style window is default
style say_label is default
style say_dialogue is default
style say_thought is say_dialogue

style namebox is default
style namebox_label is say_label


style window:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    ysize gui.textbox_height

    background Image("gui/textbox.png", xalign=0.5, yalign=1.0)

style namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height

    background Frame("gui/namebox.png", gui.namebox_borders, tile=gui.namebox_tile, xalign=gui.name_xalign)
    padding gui.namebox_borders.padding

style say_label:
    properties gui.text_properties("name", accent=True)
    xalign gui.name_xalign
    yalign 0.5

style say_dialogue:
    properties gui.text_properties("dialogue")

    xpos gui.dialogue_xpos
    xsize gui.dialogue_width
    ypos gui.dialogue_ypos


## Input screen ################################################################
##
## This screen is used to display renpy.input. The prompt parameter is used to
## pass a text prompt in.
##
## This screen must create an input displayable with id "input" to accept the
## various input parameters.
##
## https://www.renpy.org/doc/html/screen_special.html#input

screen input(prompt):
    style_prefix "input"

    window:

        vbox:
            xalign gui.dialogue_text_xalign
            xpos gui.dialogue_xpos
            xsize gui.dialogue_width
            ypos gui.dialogue_ypos

            text prompt style "input_prompt"
            input id "input"

style input_prompt is default

style input_prompt:
    xalign gui.dialogue_text_xalign
    properties gui.text_properties("input_prompt")

style input:
    xalign gui.dialogue_text_xalign
    xmaximum gui.dialogue_width


## Choice screen ###############################################################
##
## This screen is used to display the in-game choices presented by the menu
## statement. The one parameter, items, is a list of objects, each with caption
## and action fields.
##
## https://www.renpy.org/doc/html/screen_special.html#choice

screen choice(items):
    style_prefix "choice"

    vbox:
        for i in items:
            textbutton i.caption action i.action


## When this is true, menu captions will be spoken by the narrator. When false,
## menu captions will be displayed as empty buttons.
define config.narrator_menu = True


style choice_vbox is vbox
style choice_button is button
style choice_button_text is button_text

style choice_vbox:
    xalign 0.5
    ypos 450
    yanchor 0.5

    spacing gui.choice_spacing

style choice_button is default:
    properties gui.button_properties("choice_button")

style choice_button_text is default:
    properties gui.button_text_properties("choice_button")


## Quick Menu screen ###########################################################
##
## The quick menu is displayed in-game to provide easy access to the out-of-game
## menus.

screen quick_menu():

    ## Ensure this appears on top of other screens.
    zorder 100

    if quick_menu:

        hbox:
            style_prefix "quick"

            xalign 0.5
            yalign 1.0

            #textbutton _("Back") action Rollback()
            #textbutton _("History") action ShowMenu('history')
            #textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
            #textbutton _("Auto") action Preference("auto-forward", "toggle")
            #textbutton _("Save") action ShowMenu('save')
            #textbutton _("Q.Save") action QuickSave()
            #textbutton _("Q.Load") action QuickLoad()
            #textbutton _("Settings") action ShowMenu('preferences')


## This code ensures that the quick_menu screen is displayed in-game, whenever
## the player has not explicitly hidden the interface.
init python:
    config.overlay_screens.append("quick_menu")

default quick_menu = True

style quick_button is default
style quick_button_text is button_text

style quick_button:
    properties gui.button_properties("quick_button")

style quick_button_text:
    outlines [(2, "#000", 0, 0)]
    properties gui.button_text_properties("quick_button")

init python:
    def reset_data():
        ## deletes all persistent data use with caution
        for attr in dir(persistent):
            if not callable(attr) and not attr.startswith("_"):
                setattr(persistent, attr, None)

        ## deletes all save games use with caution!
        for slot in renpy.list_saved_games(fast=True):
            renpy.unlink_save(slot)
        ## a Ren'Py relaunch is nessesary
        renpy.quit(relaunch=True)

################################################################################
## Main and Game Menu Screens
################################################################################

## Navigation screen ###########################################################
##
## This screen is included in the main and game menus, and provides navigation
## to other menus, and to start the game.

screen guidescreen(gMessage):
    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            text ""
            text gMessage
            text ""
            button:
                text "{font=msi.ttf}{color=ff0000} 不 {/color}{/font}"
                action Return()
            button:
                text "{font=msi.ttf}{color=ff0000} 是的 {/color}{/font}"
                action Jump("forty")

screen guidescreen2(gMessage):
    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            text ""
            text gMessage
            text ""
            button:
                text "{font=msi.ttf}{color=ff0000}{size=50} 是的 {/color}{/font}{/size}"
                action Return()

screen guidescreen3(gMessage):
    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            text ""
            text gMessage
            text ""
            button:
                text "{font=msi.ttf}{color=ff0000} 是的 {/color}{/font}"
                action Return()
            button:
                text "{font=msi.ttf}{color=ff0000} 不 {/color}{/font}"
                action Jump("forty")

screen navigation():

    vbox:
        style_prefix "navigation"

        xpos gui.navigation_xpos
        xalign -0.99 yalign 0.5

        spacing gui.navigation_spacing -7

        if main_menu:

            textbutton _("故事") action Start() text_outlines [ (0, "#FFFFFF", 0, 0) ]:
                keyboard_focus_insets (0, 10, 0, 10)
            if persistent.finishedgame == True:

                textbutton _("夢境") action Start("epi") text_outlines [ (0, "#FFFFFF", 0, 0) ]:
                    keyboard_focus_insets (0, 10, 0, 10)
            elif persistent.epilogue == True:

                textbutton _("尾聲") action Start("epi") text_outlines [ (0, "#FFFFFF", 0, 0) ]:
                    keyboard_focus_insets (0, 10, 0, 10)

            if persistent.dlcactive == True:

                textbutton _("第二層樓") action Start("anew") text_outlines [ (0, "#FFFFFF", 0, 0) ]:
                    keyboard_focus_insets (0, 10, 0, 10)
            textbutton _("音樂") action [ShowMenu("music_room"), Function(ost.get_music_channel_info), Stop('music', fadeout=2.0), Function(ost.refresh_list)]:
                keyboard_focus_insets (0, 10, 0, 10)



        #elif main_menu:

            #textbutton _("Achievements") action ShowMenu("achievements")

        else:

            #textbutton _("History") action ShowMenu("history") text_outlines [ (0, "#FFFFFF", 0, 0) ]

            textbutton _("儲存") action ShowMenu("save") text_outlines [ (0, "#FFFFFF", 0, 0) ]:
                keyboard_focus_insets (0, 10, 0, 10)
        textbutton _("載入") action ShowMenu("load") text_outlines [ (0, "#FFFFFF", 0, 0) ]:
            keyboard_focus_insets (0, 10, 0, 10)
        textbutton _("設定") action ShowMenu("preferences") text_outlines [ (0, "#FFFFFF", 0, 0) ]:
            keyboard_focus_insets (0, 10, 0, 10)
        if _in_replay:

            textbutton _("結束重播") action EndReplay(confirm=True) text_outlines [ (0, "#FFFFFF", 0, 0) ]:
                keyboard_focus_insets (0, 10, 0, 10)
        elif not main_menu:

            textbutton _("選單") action MainMenu() text_outlines [ (0, "#FFFFFF", 0, 0) ]:
                keyboard_focus_insets (0, 10, 0, 10)

        #textbutton _("About") action ShowMenu("about") text_outlines [ (0, "#FFFFFF", 0, 0) ]

        #if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):

            ## Help isn't necessary or relevant to mobile devices.
            #textbutton _("Help") action ShowMenu("help") text_outlines [ (0, "#FFFFFF", 0, 0) ]

        if renpy.variant("pc"):

            ## The quit button is banned on iOS and unnecessary on Android and
            ## Web.
            textbutton _("退出") action Quit(confirm=not main_menu) text_outlines [ (0, "#FFFFFF", 0, 0) ]:
                keyboard_focus_insets (0, 10, 0, 10)


style navigation_button is gui_button
style navigation_button_text is gui_button_text

style navigation_button:
    size_group "navigation"
    properties gui.button_properties("navigation_button")

style navigation_button_text:
    properties gui.button_text_properties("navigation_button")


## Main Menu screen ############################################################
##
## Used to display the main menu when Ren'Py starts.
##
## https://www.renpy.org/doc/html/screen_special.html#main-menu
init python:
    import pygame
    import math


    class TrackCursor(renpy.Displayable):

        def __init__(self, child, paramod, **kwargs):

            super(TrackCursor, self).__init__()

            self.child = renpy.displayable(child)
            self.x = 0
            self.y = 0
            self.actual_x = 0
            self.actual_y = 0

            self.paramod = paramod
            self.last_st = 0



        def render(self, width, height, st, at):

            rv = renpy.Render(width, height)
            minimum_speed = 0.5
            maximum_speed = 3
            speed = 1 + minimum_speed
            mouse_distance_x = min(maximum_speed, max(minimum_speed, (self.x - self.actual_x)))
            mouse_distance_y = (self.y - self.actual_y)
            if self.x is not None:
                st_change = st - self.last_st

                self.last_st = st
                self.actual_x = math.floor(self.actual_x + ((self.x - self.actual_x) * speed * (st_change )) * self.paramod)
                self.actual_y = math.floor(self.actual_y + ((self.y - self.actual_y) * speed * (st_change)) * self.paramod)


                if mouse_distance_y <= minimum_speed:
                    mouse_distance_y = minimum_speed
                elif mouse_distance_y >= maximum_speed:
                    mouse_distance_y = maximum_speed

                cr = renpy.render(self.child, width, height, st, at)
                cw, ch = cr.get_size()
                rv.blit(cr, (self.actual_x, self.actual_y))



            renpy.redraw(self, 0)
            return rv

        def event(self, ev, x, y, st):
            hover = ev.type == pygame.MOUSEMOTION
            click = ev.type == pygame.MOUSEBUTTONDOWN
            mousefocus = pygame.mouse.get_focused()
            if hover:

                if (x != self.x) or (y != self.y) or click:
                    self.x = -x /self.paramod
                    self.y = -y /self.paramod


screen main_menu():

    ## This ensures that any other menu screen is replaced.
    tag menu

    if persistent.location == 1:
        add "gui/main_menu11.png"
    else:
        add "gui/main_menu11.png"




    add TrackCursor("gui/main_menu10_2.png", 20)
    add TrackCursor("gui/main_menu11_back.png", 28)
    add TrackCursor("gui/main_menu11_back2.png", 30)
    add TrackCursor("gui/main_menu11_back5.png", 26)
    add TrackCursor("gui/main_menu11_back3.png", 23)
    add TrackCursor("gui/main_menu11_back4.png", 20)

    add TrackCursor("gui/main_menu6.png", 17)
    add TrackCursor("gui/main_menu11_1.png", 10)
    if persistent.harbinger == True:
        add TrackCursor("gui/main_menuXXs_2s.png", 17)
        add TrackCursor("gui/main_menuXXs_1s.png", 10)
    if persistent.vaiextra2 == True:
        add TrackCursor("gui/vaii2.png", 30)
    add TrackCursor("gui/main_menuXXs.png", 50)

    add TrackCursor("gui/main_menuXX1.png", 30)
    add TrackCursor("gui/main_menuXX2.png", 35)
    add "gui/main_menu4.png"


    #add "gui/main_menu3.png"
    #add "gui/main_menu11.png"
    if persistent.saidgoodbye == True:
        add TrackCursor("gui/main_menu1_four1.png", 50)
    elif persistent.finishedgame == True:
        add TrackCursor("gui/main_menuV.png", 50)
    elif persistent.versus == True:
        add TrackCursor("gui/main_menu1_three.png", 50)
    elif persistent.vaip == True:
        add TrackCursor("gui/main_menu1_pinks.png", 50)
    elif persistent.kiryu == True:
        add TrackCursor("gui/main_menu1_ix.png", 50)
    elif persistent.replicant == True:
        add TrackCursor("gui/main_menu1_e.png", 50)
    elif persistent.oaths == True:
        add TrackCursor("gui/main_menu1_two.png", 50)
    elif persistent.completed == True:
        add TrackCursor("gui/main_menu1_zero.png", 50)
    elif persistent.allrooms == True:
        add TrackCursor("gui/main_menu1_five.png", 50)
    elif persistent.secret_end == True:
        add TrackCursor("gui/main_menu1_four.png", 50)
    else:
        add TrackCursor("gui/main_menu1_two.png", 50)


    if persistent.alldishes == True:
        add TrackCursor("gui/main_menu1_fourXX.png", 45)

    if persistent.vaiextra1 == True:
        add TrackCursor("gui/vaii1.png", 30)

    if persistent.vaiextra3 == True:
        add TrackCursor("gui/vaii3.png", 25)

    if persistent.kiryu == True:
        add TrackCursor("gui/char_2.png", 30)
    elif persistent.vaip == True:
        add TrackCursor("gui/char_1.png", 30)
    elif persistent.nujip == True:
        add TrackCursor("gui/nuji_menu.png", 30)
    elif persistent.cruseyp == True:
        add TrackCursor("gui/crusey_menu.png", 30)
    elif persistent.swazyp == True:
        add TrackCursor("gui/swazy_menu.png", 30)
    elif persistent.aftrrp == True:
        add TrackCursor("gui/aftrr_menu.png", 30)
    elif persistent.rubyp == True:
        add TrackCursor("gui/ruby_menu.png", 30)
    elif persistent.crusafixp == True:
        add TrackCursor("gui/crusafix_menu.png", 30)
    elif persistent.zayokp == True:
        add TrackCursor("gui/zayok_menu.png", 30)
    elif persistent.tsuyunop == True:
        add TrackCursor("gui/tsuyuno_menu.png", 30)
    elif persistent.tsukiip == True:
        add TrackCursor("gui/tsukii_menu.png", 30)
    add anim.Filmstrip("leaves.png", (1280,720), (1,3), 0.7, loop=True)

    ## This empty frame darkens the main menu.
    frame:
        style "main_menu_frame"

    ## The use statement includes another screen inside this one. The actual
    ## contents of the main menu are in the navigation screen.
    use navigation

    if gui.show_name:

        vbox:
            style "main_menu_vbox"

            text "[config.name!t]":
                style "main_menu_title"

            text "[config.version]":
                style "main_menu_version"


style main_menu_frame is empty
style main_menu_vbox is vbox
style main_menu_text is gui_text
style main_menu_title is main_menu_text
style main_menu_version is main_menu_text

style main_menu_frame:
    xsize 280
    yfill True

    #background "gui/main_menu2.png"

style main_menu_vbox:
    xalign 1.0
    xoffset -20
    xmaximum 800
    yalign 1.0
    yoffset -20

style main_menu_text:
    properties gui.text_properties("main_menu", accent=True)

style main_menu_title:
    properties gui.text_properties("title")

style main_menu_version:
    properties gui.text_properties("version")


## Game Menu screen ############################################################
##
## This lays out the basic common structure of a game menu screen. It's called
## with the screen title, and displays the background, title, and navigation.
##
## The scroll parameter can be None, or one of "viewport" or "vpgrid". When
## this screen is intended to be used with one or more children, which are
## transcluded (placed) inside it.

screen game_menu(title, scroll=None, yinitial=0.0):
    on 'show' action PauseAudio('music', True)
    style_prefix "game_menu"

    if main_menu:
        add gui.main_menu_background
    else:
        add gui.game_menu_background

    frame:
        style "game_menu_outer_frame"

        hbox:

            ## Reserve space for the navigation section.
            frame:
                style "game_menu_navigation_frame"

            frame:
                style "game_menu_content_frame"

                if scroll == "viewport":

                    viewport:
                        yinitial yinitial
                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True

                        side_yfill True

                        vbox:
                            transclude

                elif scroll == "vpgrid":

                    vpgrid:
                        cols 1
                        yinitial yinitial

                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True

                        side_yfill True

                        transclude

                else:

                    transclude

    use navigation

    textbutton _("返回") text_outlines [ (0, "#FFFFFF", 0, 0) ]:
        style "return_button"

        action Return()

    label title

    if main_menu:
        key "game_menu" action ShowMenu("main_menu")


style game_menu_outer_frame is empty
style game_menu_navigation_frame is empty
style game_menu_content_frame is empty
style game_menu_viewport is gui_viewport
style game_menu_side is gui_side
style game_menu_scrollbar is gui_vscrollbar

style game_menu_label is gui_label
style game_menu_label_text is gui_label_text

style return_button is navigation_button
style return_button_text is navigation_button_text

style game_menu_outer_frame:
    bottom_padding 30
    top_padding 120

    background "gui/overlay/game_menu.png"

style game_menu_navigation_frame:
    xsize 280
    yfill True

style game_menu_content_frame:
    left_margin 40
    right_margin 20
    top_margin 10

style game_menu_viewport:
    xsize 920

style game_menu_vscrollbar:
    unscrollable gui.unscrollable

style game_menu_side:
    spacing 10

style game_menu_label:
    xpos 50
    ysize 120

style game_menu_label_text:
    size gui.title_text_size
    color gui.accent_color
    yalign 0.5

style return_button:
    xpos gui.navigation_xpos
    yalign 1.0
    yoffset -30


## About screen ################################################################
##
## This screen gives credit and copyright information about the game and Ren'Py.
##
## There's nothing special about this screen, and hence it also serves as an
## example of how to make a custom screen.

screen about():

    tag menu

    ## This use statement includes the game_menu screen inside this one. The
    ## vbox child is then included inside the viewport inside the game_menu
    ## screen.
    use game_menu(_("關於"), scroll="viewport"):

        style_prefix "about"

        vbox:

            label "[config.name!t]"
            text _("版本 [config.version!t]\n")

            ## gui.about is usually set in options.rpy.
            if gui.about:
                text "[gui.about!t]\n"

            text _(" ")


style about_label is gui_label
style about_label_text is gui_label_text
style about_text is gui_text

style about_label_text:
    size gui.label_text_size


## Load and Save screens #######################################################
##
## These screens are responsible for letting the player save the game and load
## it again. Since they share nearly everything in common, both are implemented
## in terms of a third screen, file_slots.
##
## https://www.renpy.org/doc/html/screen_special.html#save https://
## www.renpy.org/doc/html/screen_special.html#load

screen save():

    tag menu

    use file_slots(_("儲存"))


screen load():

    tag menu

    use file_slots(_("載入"))


screen file_slots(title):

    default page_name_value = FilePageNameInputValue(pattern=_("Page {}"), auto=_("Automatic saves"), quick=_("Quick saves"))

    use game_menu(title):

        fixed:

            ## This ensures the input will get the enter event before any of the
            ## buttons do.
            order_reverse True

            ## The page name, which can be edited by clicking on a button.
            button:
                style "page_label"

                key_events True
                xalign 0.5
                action page_name_value.Toggle()

                input:
                    style "page_label_text"
                    value page_name_value

            ## The grid of file slots.
            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"

                xalign 0.5
                yalign 0.5

                spacing gui.slot_spacing

                for i in range(gui.file_slot_cols * gui.file_slot_rows):

                    $ slot = i + 1

                    button:
                        action FileAction(slot)

                        has vbox

                        add FileScreenshot(slot) xalign 0.5

                        text FileTime(slot, format=_("{#file_time}%A, %B %d %Y, %H:%M"), empty=_("empty slot")):
                            style "slot_time_text"

                        text FileSaveName(slot):
                            style "slot_name_text"

                        key "save_delete" action FileDelete(slot)

            ## Buttons to access other pages.
            hbox:
                style_prefix "page"

                xalign 0.5
                yalign 1.0

                spacing gui.page_spacing

                textbutton _("(") action FilePagePrevious()

                if config.has_autosave:
                    textbutton _("{#auto_page}A") action FilePage("auto")

                if config.has_quicksave:
                    textbutton _("{#quick_page}Q") action FilePage("quick")

                ## range(1, 10) gives the numbers from 1 to 9.
                for page in range(1, 10):
                    textbutton "[page]" action FilePage(page)

                textbutton _(")") action FilePageNext()


style page_label is gui_label
style page_label_text is gui_label_text
style page_button is gui_button
style page_button_text is gui_button_text

style slot_button is gui_button
style slot_button_text is gui_button_text
style slot_time_text is slot_button_text
style slot_name_text is slot_button_text

style page_label:
    xpadding 50
    ypadding 3

style page_label_text:
    text_align 0.5
    layout "subtitle"
    hover_color gui.hover_color

style page_button:
    properties gui.button_properties("page_button")

style page_button_text:
    properties gui.button_text_properties("page_button")

style slot_button:
    properties gui.button_properties("slot_button")

style slot_button_text:
    properties gui.button_text_properties("slot_button")


## Preferences screen ##########################################################
##
## The preferences screen allows the player to configure the game to better suit
## themselves.
##
## https://www.renpy.org/doc/html/screen_special.html#preferences

screen preferences():

    tag menu

    use game_menu(_("偏好设置"), scroll="viewport"):

        vbox:

            hbox:
                box_wrap True

                if renpy.variant("pc") or renpy.variant("web"):

                    vbox:
                        style_prefix "radio"
                        label _("显示")
                        textbutton _("窗户") action Preference("display", "window")
                        textbutton _("全屏") action Preference("display", "fullscreen")


                vbox:
                    style_prefix "check"
                    label _("跳过")
                    #textbutton _("Unseen Text") action Preference("skip", "toggle")
                    textbutton _("选择之后") action Preference("after choices", "toggle")
                    textbutton _("过渡") action InvertSelected(Preference("transitions", "toggle"))
                vbox:
                    textbutton _("艺术作品") action ShowMenu("album") text_outlines [ (0, "#FFFFFF", 0, 0) ] text_size 25
                    textbutton _("信息") action ShowMenu("about") text_outlines [ (0, "#FFFFFF", 0, 0) ] text_size 25
                    textbutton _("控制") action ShowMenu("help") text_outlines [ (0, "#FFFFFF", 0, 0) ] text_size 25
                    textbutton _("重置") action Confirm("All saved data will be deleted. Do you want to reset?", Function(reset_data)) text_size 25
                    textbutton _(" ") action ShowMenu("help") text_outlines [ (0, "#FFFFFF", 0, 0) ] text_size 10
                    #textbutton _("English") action Language(None)
                    #textbutton _("中文") action Language("chinese")

                ## Additional vboxes of type "radio_pref" or "check_pref" can be
                ## added here, to add additional creator-defined preferences.

            null height (4 * gui.pref_spacing)

            hbox:
                style_prefix "slider"
                box_wrap True

                vbox:

                    label _("文本速度")

                    bar value Preference("text speed")

                    label _("自动转发时间")

                    bar value Preference("auto-forward time")

                vbox:

                    if config.has_music:
                        label _("音乐音量")

                        hbox:
                            bar value Preference("music volume")

                    if config.has_sound:

                        label _("音量")

                        hbox:
                            bar value Preference("sound volume")

                            if config.sample_sound:
                                textbutton _("Test") action Play("sound", config.sample_sound)


                    if config.has_voice:
                        label _("文本转语音音量")

                        hbox:
                            bar value Preference("voice volume")

                            if config.sample_voice:
                                textbutton _("Test") action Play("voice", config.sample_voice)

                    if config.has_music or config.has_sound or config.has_voice:
                        null height gui.pref_spacing

                        textbutton _("静音全部"):
                            action Preference("all mute", "toggle")
                            style "mute_all_button"


style pref_label is gui_label
style pref_label_text is gui_label_text
style pref_vbox is vbox

style radio_label is pref_label
style radio_label_text is pref_label_text
style radio_button is gui_button
style radio_button_text is gui_button_text
style radio_vbox is pref_vbox

style check_label is pref_label
style check_label_text is pref_label_text
style check_button is gui_button
style check_button_text is gui_button_text
style check_vbox is pref_vbox

style slider_label is pref_label
style slider_label_text is pref_label_text
style slider_slider is gui_slider
style slider_button is gui_button
style slider_button_text is gui_button_text
style slider_pref_vbox is pref_vbox

style mute_all_button is check_button
style mute_all_button_text is check_button_text

style pref_label:
    top_margin gui.pref_spacing
    bottom_margin 2

style pref_label_text:
    yalign 1.0

style pref_vbox:
    xsize 225

style radio_vbox:
    spacing gui.pref_button_spacing

style radio_button:
    properties gui.button_properties("radio_button")
    foreground "gui/button/radio_[prefix_]foreground.png"

style radio_button_text:
    properties gui.button_text_properties("radio_button")

style check_vbox:
    spacing gui.pref_button_spacing

style check_button:
    properties gui.button_properties("check_button")
    foreground "gui/button/check_[prefix_]foreground.png"

style check_button_text:
    properties gui.button_text_properties("check_button")

style slider_slider:
    xsize 350

style slider_button:
    properties gui.button_properties("slider_button")
    yalign 0.5
    left_margin 10

style slider_button_text:
    properties gui.button_text_properties("slider_button")

style slider_vbox:
    xsize 450


## History screen ##############################################################
##
## This is a screen that displays the dialogue history to the player. While
## there isn't anything special about this screen, it does have to access the
## dialogue history stored in _history_list.
##
## https://www.renpy.org/doc/html/history.html

screen history():

    tag menu

    ## Avoid predicting this screen, as it can be very large.
    predict False

    use game_menu(_("History"), scroll=("vpgrid" if gui.history_height else "viewport"), yinitial=1.0):

        style_prefix "history"

        for h in _history_list:

            window:

                ## This lays things out properly if history_height is None.
                has fixed:
                    yfit True

                if h.who:

                    label h.who:
                        style "history_name"
                        substitute False

                        ## Take the color of the who text from the Character, if
                        ## set.
                        if "color" in h.who_args:
                            text_color h.who_args["color"]

                $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
                text what:
                    substitute False

        if not _history_list:
            label _("The dialogue history is empty.")


## This determines what tags are allowed to be displayed on the history screen.

define gui.history_allow_tags = { "alt", "noalt" }


style history_window is empty

style history_name is gui_label
style history_name_text is gui_label_text
style history_text is gui_text

style history_text is gui_text

style history_label is gui_label
style history_label_text is gui_label_text

style history_window:
    xfill True
    ysize gui.history_height

style history_name:
    xpos gui.history_name_xpos
    xanchor gui.history_name_xalign
    ypos gui.history_name_ypos
    xsize gui.history_name_width

style history_name_text:
    min_width gui.history_name_width
    text_align gui.history_name_xalign

style history_text:
    xpos gui.history_text_xpos
    ypos gui.history_text_ypos
    xanchor gui.history_text_xalign
    xsize gui.history_text_width
    min_width gui.history_text_width
    text_align gui.history_text_xalign
    layout ("subtitle" if gui.history_text_xalign else "tex")

style history_label:
    xfill True

style history_label_text:
    xalign 0.5


## Help screen #################################################################
##
## A screen that gives information about key and mouse bindings. It uses other
## screens (keyboard_help, mouse_help, and gamepad_help) to display the actual
## help.

screen help():

    tag menu

    default device = "keyboard"

    use game_menu(_("帮助"), scroll="viewport"):

        style_prefix "help"

        vbox:
            spacing 15

            hbox:

                textbutton _("键盘") action SetScreenVariable("device", "keyboard")
                textbutton _("电脑鼠标") action SetScreenVariable("device", "mouse")

                if GamepadExists():
                    textbutton _("游戏手柄") action SetScreenVariable("device", "gamepad")

            if device == "keyboard":
                use keyboard_help
            elif device == "mouse":
                use mouse_help
            elif device == "gamepad":
                use gamepad_help


screen keyboard_help():

    hbox:
        label _("Enter")
        text _("(RRPG) 互动.\n(STORY) 推进对话并激活界面。.")

    hbox:
        label _("空格")
        text _("(RPG) 互动.\n(STORY) 推进对话而不选择选项。")

    hbox:
        label _("方向键")
        text _("(RPG) 移动。\n(STORY) 导航界面。.")

    hbox:
        label _("ESC")
        text _("进入游戏菜单。")

    hbox:
        label _("Ctrl")
        text _("按住时跳过对话。")

    hbox:
        label _("Shift")
        text _("(RPG) 按住时冲刺。.")

    hbox:
        label _("Tab")
        text _("切换对话跳过状态。.")

    hbox:
        label _("Page Up")
        text _("回溯至先前对话.")

    hbox:
        label _("Page Down")
        text _("前进至后续对话。")

    hbox:
        label "H"
        text _("隐藏用户界面.")

    hbox:
        label "M"
        text _("(在'故事2DLC'中) 按下时缩小地图")

    hbox:
        label "S"
        text _("截取屏幕截图。")

    hbox:
        label "V"
        text _("切换辅助语音提示。可能在中国无法使用。")


screen mouse_help():

    hbox:
        label _("左键点击")
        text _("推进对话并激活界面。")

    hbox:
        label _("中键点击")
        text _("隐藏用户界面。")

    hbox:
        label _("鼠标滚轮上滚动\n点击回溯侧")
        text _("回溯至先前对话。")

    hbox:
        label _("鼠标滚轮下推")
        text _("滚动至后续对话框。")


screen gamepad_help():

    hbox:
        label _("右扳机键,\nA键")
        text _("(RPG) 互动.\n(STORY) 推进对话并激活\n界面。")

    hbox:
        label _("左扳机键")
        text _("回溯至先前对话。")

    hbox:
        label _("右肩键")
        text _("(在'故事2DLC'中)切换地图缩放（缩小）")

    hbox:
        label _("左肩键")
        text _("(在'故事2DLC'中) 切换地图缩放（放大）")


    hbox:
        label _("方向键、摇杆")
        text _("(RPG) 移动.\n (STORY) 导航界面.")

    hbox:
        label _("开始键")
        text _("进入游戏菜单。")

    hbox:
        label _("Y键/顶部按钮")
        text _("隐藏用户界面。")

    #textbutton _("Calibrate") action GamepadCalibrate()


style help_button is gui_button
style help_button_text is gui_button_text
style help_label is gui_label
style help_label_text is gui_label_text
style help_text is gui_text

style help_button:
    properties gui.button_properties("help_button")
    xmargin 8

style help_button_text:
    properties gui.button_text_properties("help_button")

style help_label:
    xsize 250
    right_padding 20

style help_label_text:
    size gui.text_size
    xalign 1.0
    text_align 1.0



################################################################################
## Additional screens
################################################################################


## Confirm screen ##############################################################
##
## The confirm screen is called when Ren'Py wants to ask the player a yes or no
## question.
##
## https://www.renpy.org/doc/html/screen_special.html#confirm

screen confirm(message, yes_action, no_action):

    ## Ensure other screens do not get input while this screen is displayed.
    modal True

    zorder 200

    style_prefix "confirm"

    add "gui/overlay/confirm.png"

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 30

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("是的") action yes_action
                textbutton _("不") action no_action

    ## Right-click and escape answer "no".
    key "game_menu" action no_action


style confirm_frame is gui_frame
style confirm_prompt is gui_prompt
style confirm_prompt_text is gui_prompt_text
style confirm_button is gui_medium_button
style confirm_button_text is gui_medium_button_text

style confirm_frame:
    background Frame([ "gui/confirm_frame.png", "gui/frame.png"], gui.confirm_frame_borders, tile=gui.frame_tile)
    padding gui.confirm_frame_borders.padding
    xalign .5
    yalign .5

style confirm_prompt_text:
    text_align 0.5
    layout "subtitle"

style confirm_button:
    properties gui.button_properties("confirm_button")

style confirm_button_text:
    properties gui.button_text_properties("confirm_button")


## Skip indicator screen #######################################################
##
## The skip_indicator screen is displayed to indicate that skipping is in
## progress.
##
## https://www.renpy.org/doc/html/screen_special.html#skip-indicator

screen skip_indicator():

    zorder 100
    style_prefix "skip"

    frame:

        hbox:
            spacing 6

            text _("加速...")
screen money:

    zorder 100

    style_prefix "money"

    frame:

        hbox:
            spacing 6
            ypos 0.2

            text "您是： [location]"

screen item:
        add "itemhud.png"
        if persistent.item_keyring == True:
            add "item keyring.png"

screen kenn:
        add "gui/kenn.png"

screen bgintro:
        add "bg b.png"





## This transform is used to blink the arrows one after another.
transform delayed_blink(delay, cycle):
    alpha .5

    pause delay

    block:
        linear .2 alpha 1.0
        pause .2
        linear .2 alpha 0.5
        pause (cycle - .4)
        repeat


style skip_frame is empty
style money_frame is empty
style skip_text is gui_text
style skip_triangle is skip_text

style skip_frame:
    ypos gui.skip_ypos
    background Frame("gui/skip.png", gui.skip_frame_borders, tile=gui.frame_tile)
    padding gui.skip_frame_borders.padding

style money_frame:
    ypos 0.065
    background Frame("gui/money.png", gui.skip_frame_borders, tile=gui.frame_tile)
    padding gui.skip_frame_borders.padding


style gui_frame:
    ypos 0.065
    background Frame("gui/money.png", gui.skip_frame_borders, tile=gui.frame_tile)
    padding gui.skip_frame_borders.padding

style skip_text:
    size gui.notify_text_size

style skip_triangle:
    ## We have to use a font that has the BLACK RIGHT-POINTING SMALL TRIANGLE
    ## glyph in it.
    font "DejaVuSans.ttf"


## Notify screen ###############################################################
##
## The notify screen is used to show the player a message. (For example, when
## the game is quicksaved or a screenshot has been taken.)
##
## https://www.renpy.org/doc/html/screen_special.html#notify-screen

screen notify(message):

    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        text "[message!tq]"

    timer 2 action Hide('notify')


transform notify_appear:
    on show:
        alpha 0
        linear .25 alpha 1.0
    on hide:
        linear .5 alpha 0.0


style notify_frame is empty
style notify_text is gui_text

style notify_frame:
    ypos gui.notify_ypos

    background Frame("gui/notify.png", gui.notify_frame_borders, tile=gui.frame_tile)
    padding gui.notify_frame_borders.padding

style notify_text:
    properties gui.text_properties("notify")
    font "msi.ttf"
    color "#ffFFFF"

## NVL screen ##################################################################
##
## This screen is used for NVL-mode dialogue and menus.
##
## https://www.renpy.org/doc/html/screen_special.html#nvl


screen nvl(dialogue, items=None):

    window:
        style "nvl_window"

        has vbox:
            spacing gui.nvl_spacing

        ## Displays dialogue in either a vpgrid or the vbox.
        if gui.nvl_height:

            vpgrid:
                cols 1
                yinitial 1.0

                use nvl_dialogue(dialogue)

        else:

            use nvl_dialogue(dialogue)

        ## Displays the menu, if given. The menu may be displayed incorrectly if
        ## config.narrator_menu is set to True, as it is above.
        for i in items:

            textbutton i.caption:
                action i.action
                style "nvl_button"

    add SideImage() xalign 0.0 yalign 1.0


screen nvl_dialogue(dialogue):

    for d in dialogue:

        window:
            id d.window_id

            fixed:
                yfit gui.nvl_height is None

                if d.who is not None:

                    text d.who:
                        id d.who_id

                text d.what:
                    id d.what_id


## This controls the maximum number of NVL-mode entries that can be displayed at
## once.
define config.nvl_list_length = gui.nvl_list_length

style nvl_window is default
style nvl_entry is default

style nvl_label is say_label
style nvl_dialogue is say_dialogue

style nvl_button is button
style nvl_button_text is button_text

style nvl_window:
    xfill True
    yfill True

    background "gui/nvl.png"
    padding gui.nvl_borders.padding

style nvl_entry:
    xfill True
    ysize gui.nvl_height

style nvl_label:
    xpos gui.nvl_name_xpos
    xanchor gui.nvl_name_xalign
    ypos gui.nvl_name_ypos
    yanchor 0.0
    xsize gui.nvl_name_width
    min_width gui.nvl_name_width
    text_align gui.nvl_name_xalign

style nvl_dialogue:
    xpos gui.nvl_text_xpos
    xanchor gui.nvl_text_xalign
    ypos gui.nvl_text_ypos
    xsize gui.nvl_text_width
    min_width gui.nvl_text_width
    text_align gui.nvl_text_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_thought:
    xpos gui.nvl_thought_xpos
    xanchor gui.nvl_thought_xalign
    ypos gui.nvl_thought_ypos
    xsize gui.nvl_thought_width
    min_width gui.nvl_thought_width
    text_align gui.nvl_thought_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_button:
    properties gui.button_properties("nvl_button")
    xpos gui.nvl_button_xpos
    xanchor gui.nvl_button_xalign

style nvl_button_text:
    properties gui.button_text_properties("nvl_button")



################################################################################
## Mobile Variants
################################################################################

style pref_vbox:
    variant "medium"
    xsize 450

## Since a mouse may not be present, we replace the quick menu with a version
## that uses fewer and bigger buttons that are easier to touch.
screen quick_menu():
    variant "touch"

    zorder 100

    if quick_menu:

        hbox:
            style_prefix "quick"

            xalign 0.5
            yalign 1.0

            textbutton _("Back") action Rollback()
            textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("Auto") action Preference("auto-forward", "toggle")
            textbutton _("Menu") action ShowMenu()


style window:
    variant "small"
    background "gui/phone/textbox.png"

style radio_button:
    variant "small"
    foreground "gui/phone/button/radio_[prefix_]foreground.png"

style check_button:
    variant "small"
    foreground "gui/phone/button/check_[prefix_]foreground.png"

style nvl_window:
    variant "small"
    background "gui/phone/nvl.png"

style main_menu_frame:
    variant "small"
    background "gui/phone/overlay/main_menu.png"

style game_menu_outer_frame:
    variant "small"
    background "gui/phone/overlay/game_menu.png"

style game_menu_navigation_frame:
    variant "small"
    xsize 340

style game_menu_content_frame:
    variant "small"
    top_margin 0

style pref_vbox:
    variant "small"
    xsize 400

transform my_movement:
    linear 0.4 zoom 1.01 xoffset 1
    linear 0.4 zoom 1.0 xoffset 0
    repeat

style bar:
    variant "small"
    ysize gui.bar_size
    left_bar Frame("gui/phone/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/phone/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    variant "small"
    xsize gui.bar_size
    top_bar Frame("gui/phone/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/phone/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    variant "small"
    ysize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    variant "small"
    xsize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    variant "small"
    ysize gui.slider_size
    base_bar Frame("gui/phone/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/horizontal_[prefix_]thumb.png"

style vslider:
    variant "small"
    xsize gui.slider_size
    base_bar Frame("gui/phone/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/vertical_[prefix_]thumb.png"

style slider_vbox:
    variant "small"
    xsize None

style slider_slider:
    variant "small"
    xsize 600

#Hey Renpy I got some music tracks...
init python:
    # Step 1. Create a MusicRoom instance.
    mr = MusicRoom(fadeout=1.0)
    # Step 2. Add music files.
    mr.add("1promise.mp3", always_unlocked=True)
    mr.add("2suffocate.mp3", always_unlocked=True)
    mr.add("3maybe.mp3", always_unlocked=True)
    mr.add("4wake.mp3", always_unlocked=True)
    mr.add("5nerve.mp3", always_unlocked=True)
    mr.add("6home.mp3", always_unlocked=True)
    mr.add("out.mp3", always_unlocked=False)
    mr.add("7sketch.mp3", always_unlocked=True)
    mr.add("sil.mp3", always_unlocked=True)
    #mr.add("music/insecure.ogg", always_unlocked=True)
    #mr.add("music/explore.ogg", always_unlocked=True)

#Hey Renpy now I gotta make a player to play em...
screen music_room:

    tag menu
    add "gui/music.png" #background image
    use navigation

    frame:
        background None #this will get rid of the frame's... frame, and its black background.
        xpos 350
        ypos 500

        has vbox
        textbutton _("{size=35}return to the title screen{/size}") action Return()

    frame:
        background None
        xpos 350
        ypos 175
        viewport id "vp":
            mousewheel True #Enable the use of your mousewheel
            draggable True #Allow you to drag the content up and down
            ymaximum 400 #The height of your viewport, you might want bigger number, and maybe an 'xmaximum' too.

            vbox: #Will align things vertically for you, I prefer this over 'has vbox', but you do you. They do the same thing.
                textbutton "promise i won't" action mr.Play("1promise.mp3")
                textbutton "suffocate" action mr.Play("2suffocate.mp3")
                textbutton "maybe i'm afraid" action mr.Play("3maybe.mp3")
                textbutton "i'll wake up crying" action mr.Play("4wake.mp3")
                textbutton "the nerve to" action mr.Play("5nerve.mp3")
                textbutton "come home" action mr.Play("6home.mp3")
                textbutton "" action mr.Play("out.mp3")
                textbutton "(click to stop audio)" action mr.Play("sil.mp3")






            #textbutton "Track 3" action mr.Play("audio/file 3.ogg")
            #textbutton "Track 4" action mr.Play("audio/file 4.ogg")
            #textbutton "Track 5" action mr.Play("audio/file 5.ogg")
            #...
            #textbutton "Track 100" action mr.Play("audio/file 100.ogg")
            #Add as many as you need.


# my shit

screen coin_display():
    if show_coins:
        frame at fadein:  # <== this is the key change
            add "coins_1.png"
            background None
        frame at fadein:
            align (1.0, 0.0)
            padding (10, 35)
            background None

            text "硬币: [persistent.coins]" font "core.otf" size 30 color "#000000" outlines [(2, "#FFFFFF", 0, 0)]

screen key_listener():
    # Press events
    key "keydown_m" action Function(lambda: pink_otm_current_camera.set_zoom(0.7))
    key "pad_rightshoulder_press" action Function(toggle_zoom_out)
    key "pad_leftshoulder_press" action Function(toggle_zoom_in_further)
    key "keydown_K_m" action Function(lambda: pink_otm_current_camera.set_zoom(0.7))

    # Release events
    key "keyup_m" action Function(lambda: pink_otm_current_camera.set_zoom(1.6))
    key "keyup_K_m" action Function(lambda: pink_otm_current_camera.set_zoom(1.6))
