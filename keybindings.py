import curses
# Used for scrolling through post headers and a post
scrollVerticalKeys={
    ord("w"):"scrollUp",
    ord("s"):"scrollDown",
    ord("t"):"scrollTop",
    ord("b"):"scrollBottom",
    curses.KEY_UP:"scrollUp",
    curses.KEY_DOWN:"scrollDown"
}
# Used for scrolling between posts
scrollHorizontalKeys={
    ord("a"):"scrollLeft",
    ord("d"):"scrollRight",
    curses.KEY_LEFT:"scrollLeft",
    curses.KEY_RIGHT:"scrollRight"
}

# Used for controlling the terminal screen
controlKeys={
    ord("q"):"exit",
    ord("r"):"refresh",
    curses.KEY_RESIZE:"resize"
}

# Used for interacting with a post
postKeys={ 
    ord("h"):"help",
    ord("o"):"open",
    ord("c"):"copy",
    ord("m"):"message",
    ord("u"):"url",
    ord("i"):"image"
}

# Used for selecting a search and editing searches
editKeys={
    ord("e"):"enter",
    ord("v"):"view",
    ord("a"):"add",
    ord("d"):"delete"
}