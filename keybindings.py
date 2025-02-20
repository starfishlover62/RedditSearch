"""
Keybindings to be used by different functions. Update the part before the
colon to change the binding. The key must be placed inside double quotes
inside of ord(). Keys must also be the lowercase version.
Example:
    Good            Bad
    ord("w"):       ord("W")
"""
import curses
# Used for scrolling through post headers and a post
scrollVerticalKeysDefault={
    curses.KEY_UP:"scrollUp",
    curses.KEY_DOWN:"scrollDown"
}

scrollVerticalKeys={
    ord("w"):"scrollUp",
    ord("s"):"scrollDown",
    ord("t"):"scrollTop",
    ord("b"):"scrollBottom",
}

# Used for scrolling between posts
scrollHorizontalKeys={
    ord("a"):"scrollLeft",
    ord("d"):"scrollRight"
}
scrollHorizontalKeysDefault={
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
