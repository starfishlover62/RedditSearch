import curses
# Used for scrolling through post headers and a post
scrollKeys={ord("w"):"scrollUp",
            ord("s"):"scrollDown",
            ord("a"):"scrollLeft",
            ord("d"):"scrollRight",
            ord("t"):"scrollTop",
            ord("b"):"scrollBottom",
            curses.KEY_UP:"scrollUp",
            curses.KEY_DOWN:"scrollDown",
            curses.KEY_LEFT:"scrollLeft",
            curses.KEY_RIGHT:"scrollRight"}

# Used for controlling the terminal screen
controlKeys={ord("q"):"exit",
            ord("r"):"refresh",
            curses.KEY_RESIZE:"resize"}

# Used for interacting with a post
postKeys={  ord("h"):"help",
            ord("o"):"open",
            ord("c"):"copy",
            ord("m"):"message",
            ord("u"):"url",
            ord("i"):"image"}

# Used for selecting a search and editing searches
treekKeys={ ord("e"):"enter",
            ord("v"):"view"}