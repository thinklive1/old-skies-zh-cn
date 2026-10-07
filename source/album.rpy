init python:
    gallery = Gallery()

    gallery.button("c0")
    gallery.image("c0")
    gallery.condition("persistent.act0_done")

    gallery.button("c1")
    gallery.image("c1")
    gallery.condition("persistent.act1_done")

    gallery.button("c2")
    gallery.image("c2")
    gallery.condition("persistent.act2_done")

    gallery.button("c3")
    gallery.image("c3")
    gallery.condition("persistent.act3_done")

    gallery.button("c4")
    gallery.image("c4")
    gallery.condition("persistent.act4_done")

    gallery.button("c5")
    gallery.image("c5")
    gallery.condition("persistent.act5_done")

    gallery.button("c6")
    gallery.image("c6")
    gallery.condition("persistent.act6_done")

    gallery.button("manga")
    gallery.image("m1")
    gallery.image("m2")
    gallery.image("m3")
    gallery.image("m4")
    gallery.image("m5")



screen album:
    tag menu
    add "images/CustomUI/bg gallery.png"

    hbox:
        xalign 0.5
        yalign 0.5
        spacing 30
        grid 4 2:
            add gallery.make_button(name="c0",unlocked="CGs/small/c0.png",locked="CGs/small/locked.png")
            add gallery.make_button(name="c1",unlocked="CGs/small/c1.png",locked="CGs/small/locked.png")
            add gallery.make_button(name="c2",unlocked="CGs/small/c2.png",locked="CGs/small/locked.png")
            add gallery.make_button(name="c3",unlocked="CGs/small/c3.png",locked="CGs/small/locked.png")
            add gallery.make_button(name="c4",unlocked="CGs/small/c4.png",locked="CGs/small/locked.png")
            add gallery.make_button(name="c5",unlocked="CGs/small/c5.png",locked="CGs/small/locked.png")
            add gallery.make_button(name="c6",unlocked="CGs/small/c6.png",locked="CGs/small/locked.png")
            add gallery.make_button(name="manga",unlocked="CGs/small/m0.png",locked="CGs/small/locked.png")

            spacing 15
        textbutton "return" action Return()
