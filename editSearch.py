import curses

import config
import functions
import page as p
import scroll
import tree

class EditSearch:
    def __init__(self,screen,search,minCols=80,minLines=24,launch=True):
        self.update(screen,search,minCols,minLines)
        self.subreddit = None
        
        if launch:
            self.editSearch()
    
    def update(self,screen=None,search=None,minCols=None,minLines=None):
        if screen is not None:
            self.screen = screen
        if search is not None:
            self.search = search
        if minCols is not None:
            self.minCols = minCols
        if minLines is not None:
            self.minLines = minLines

    def editSearch(self):
    
        if self.search.subreddits is not None:

            toolTipTypes = {
                "main": [
                    scroll.Line(
                        ["<-- Line %i/%i -- >", "(press e to select a subreddit to edit)"],
                        [0, "max-40"],
                        curses.COLS,
                    )
                ],
                "press": [
                    scroll.Line(
                        ["Enter a subreddit number (1-%i), then press enter:", "(press q to exit)"],
                        [0, "max-18"],
                        curses.COLS,
                    )
                ],
                "enter": [
                    scroll.Line(
                        ["Enter a subreddit number (1-%i), then press enter:", "(enter q to exit)"],
                        [0, "max-18"],
                        curses.COLS,
                    )
                ],
            }
            toolTip = scroll.ToolTip(toolTipTypes["main"])
            scrollingList = scroll.ScrollingList(self.screen,self.viewSearchTree(self.search),tooltip=toolTip)

            page = p.Page(screen=self.screen,scrollingList=scrollingList,tooltip=toolTip,tooltipTypes=toolTipTypes,onUpdate=self.viewSearchTree,content=self.search,minRows=self.minLines,minCols=self.minCols)
            page.switchTooltip("main")
            resized = False
            # browsePage.updateContent()
                    
            while True:
                # Updates the tooltip, and prints the headers to the screen
                page.refreshTooltip("main",[page.currentLine() + 1, scrollingList.maxLine + 1],print=True)

                # Gets input from the user

                input = functions.eventListener(self.screen)

                match input:
                    case "timeout":
                        continue
                    case "exit":
                        return resized
                    case "enter":
                        # Updates the tooltip and places the cursor for input
                        page.refreshTooltip("press",(len(self.search.subreddits)),print=True)

                        functions.placeCursor(self.screen, x=50, y=curses.LINES - 1)
                        c = self.screen.getch()  # Gets the character they type
                        if c == ord("q"):  # Immediately exits if they pressed q
                            continue

                        else:  # Otherwise
                            # Update prompt to tell them to 'enter q" instead of 'press q"
                            page.refreshTooltip("enter",(len(self.search.subreddits)),print=True)
                            string = functions.getInput(
                                screen=self.screen, page=scrollingList, tooltip=toolTip, unget=c, col=50
                            )

                            # Attempts to convert their input into an integer.
                            val = 0
                            try:
                                val = int(string) - 1
                            except ValueError:
                                continue

                            # Checks if it is within the bounds of post numbersS
                            if val >= 0 and val < len(self.search.subreddits):
                                if self.editSubreddit(val):
                                    page.resize()
                    case _:
                        if page.manipulate(input)  == 1:
                            resized = True  


    def editSubreddit(self,index):
        self.subreddit = self.search.subreddits[index]
        toolTipTypes = {
            "main": [
                scroll.Line(
                    ["<-- Line %i/%i -- >", "(press e to select a filter to edit)"],
                    [0, "max-37"],
                    curses.COLS,
                )
            ],
            "press": [
                scroll.Line(
                    ["Enter a filter number (1-%i), then press enter:", "(press q to exit)"],
                    [0, "max-18"],
                    curses.COLS,
                )
            ],
            "enter": [
                scroll.Line(
                    ["Enter a filter number (1-%i), then press enter:", "(enter q to exit)"],
                    [0, "max-18"],
                    curses.COLS,
                )
            ],
        }
        toolTip = scroll.ToolTip(toolTipTypes["main"])
        scrollingList = scroll.ScrollingList(self.screen,self.viewSubTree(self.search.subreddits[index]),tooltip=toolTip)

        page = p.Page(screen=self.screen,scrollingList=scrollingList,tooltip=toolTip,tooltipTypes=toolTipTypes,onUpdate=self.viewSubTree,content=self.search.subreddits[index],minRows=self.minLines,minCols=self.minCols)
        page.switchTooltip("main")

        resized = False

        while True:
            # Updates the tooltip, and prints the headers to the screen
            page.refreshTooltip("main",[page.currentLine() + 1, scrollingList.maxLine + 1],print=True)

            # Gets input from the user

            filterInput = functions.eventListener(self.screen)

            match filterInput:
                case "timeout":
                    continue
                case "exit":
                    return resized
                case "enter":
                    # Updates the tooltip and places the cursor for input
                    page.refreshTooltip("press",(6),print=True)

                    functions.placeCursor(self.screen, x=48, y=curses.LINES - 1)
                    c = self.screen.getch()  # Gets the character they type
                    if c == ord("q"):  # Immediately exits if they pressed q
                        continue

                    else:  # Otherwise
                        # Update prompt to tell them to 'enter q" instead of 'press q"
                        page.refreshTooltip("enter",(6),print=True)
                        string = functions.getInput(
                            screen=self.screen, page=scrollingList, tooltip=toolTip, unget=c, col=48
                        )

                        # Attempts to convert their input into an integer.
                        val = 0
                        try:
                            val = int(string) - 1
                        except ValueError:
                            continue

                        # Checks if it is within the bounds of post numbersS
                        if val >= 0 and val < 6:
                            if self.editFilter(index,val):
                                page.resize()
                                resized = True
                case _:
                    if page.manipulate(filterInput) == 1:
                        resized = True


    def editFilter(self,index,filterValue):
        toolTipTypes = {
            "main": [
                scroll.Line(
                    ["<-- Line %i/%i -- >", "(press e to select a filter to edit)"],
                    [0, "max-37"],
                    curses.COLS,
                )
            ],
            "press": [
                scroll.Line(
                    ["Enter a filter number (1-%i), then press enter:", "(press q to exit)"],
                    [0, "max-18"],
                    curses.COLS,
                )
            ],
            "enter": [
                scroll.Line(
                    ["Enter a filter number (1-%i), then press enter:", "(enter q to exit)"],
                    [0, "max-18"],
                    curses.COLS,
                )
            ],
        }
        toolTip = scroll.ToolTip(toolTipTypes["main"])
        scrollingList = scroll.ScrollingList(self.screen,"",tooltip=toolTip)
        page = p.Page()
        content = None
        match filterValue:
            case 0:
                content = self.search.subreddits[index].titleWL
                page.update(screen=self.screen,scrollingList=scrollingList,tooltip=toolTip,tooltipTypes=toolTipTypes,onUpdate=self.treeWT,content=content,minRows=self.minLines,minCols=self.minCols)
            case 1:
                content = self.search.subreddits[index].titleBL
                page.update(screen=self.screen,scrollingList=scrollingList,tooltip=toolTip,tooltipTypes=toolTipTypes,onUpdate=self.treeBT,content=content,minRows=self.minLines,minCols=self.minCols)
            case 2:
                content = self.search.subreddits[index].flairWL
                page.update(screen=self.screen,scrollingList=scrollingList,tooltip=toolTip,tooltipTypes=toolTipTypes,onUpdate=self.treeWF,content=content,minRows=self.minLines,minCols=self.minCols)
            case 3:
                content = self.search.subreddits[index].flairBL
                page.update(screen=self.screen,scrollingList=scrollingList,tooltip=toolTip,tooltipTypes=toolTipTypes,onUpdate=self.treeBF,content=content,minRows=self.minLines,minCols=self.minCols)
            case 4:
                content = self.search.subreddits[index].postWL
                page.update(screen=self.screen,scrollingList=scrollingList,tooltip=toolTip,tooltipTypes=toolTipTypes,onUpdate=self.treeWP,content=content,minRows=self.minLines,minCols=self.minCols)
            case 5:
                content = self.search.subreddits[index].postBL
                page.update(screen=self.screen,scrollingList=scrollingList,tooltip=toolTip,tooltipTypes=toolTipTypes,onUpdate=self.treeBP,content=content,minRows=self.minLines,minCols=self.minCols)
            case _:
                return False
        page.updateContent(content)
        page.switchTooltip("main")
        resized = False
        
        while True:
            # Updates the tooltip, and prints the headers to the screen
            page.refreshTooltip("main",[page.currentLine() + 1, scrollingList.maxLine + 1],print=True)

            # Gets input from the user

            input = functions.eventListener(self.screen)

            match input:
                case "timeout":
                    continue
                case "exit":
                    return resized
                case "enter":
                    # Updates the tooltip and places the cursor for input
                    page.refreshTooltip("press",len(content),print=True)

                    functions.placeCursor(self.screen, x=48, y=curses.LINES - 1)
                    c = self.screen.getch()  # Gets the character they type
                    if c == ord("q"):  # Immediately exits if they pressed q
                        continue

                    else:  # Otherwise
                        # Update prompt to tell them to 'enter q" instead of 'press q"
                        page.refreshTooltip("enter",len(content),print=True)
                        string = functions.getInput(
                            screen=self.screen, page=scrollingList, tooltip=toolTip, unget=c, col=48
                        )

                        # Attempts to convert their input into an integer.
                        val = 0
                        try:
                            val = int(string) - 1
                        except ValueError:
                            continue

                        # Checks if it is within the bounds of post numbersS
                        if val >= 0 and val < 6:
                            pass
                case _:
                    if page.manipulate(input) == 1:
                        resized = True



    def viewSearchTree(self,search):
        return tree.searchTree(search,curses.COLS,config.fancy_characters,enumerate=True)

    def viewSubTree(self,subreddit):
        return tree.subTree(subreddit,curses.COLS,config.fancy_characters)

    def treeWT(self,filterContent):
        return tree.filterTree(self.subreddit.name,"Title whitelist",filterContent,curses.COLS,config.fancy_characters,True)
    def treeBT(self,filterContent):
        return tree.filterTree(self.subreddit.name,"Title blacklist",filterContent,curses.COLS,config.fancy_characters,True)
    def treeWF(self,filterContent):
        return tree.filterTree(self.subreddit.name,"Flair whitelist",filterContent,curses.COLS,config.fancy_characters,True)
    def treeBF(self,filterContent):
        return tree.filterTree(self.subreddit.name,"Flair blacklist",filterContent,curses.COLS,config.fancy_characters,True)
    def treeWP(self,filterContent):
        return tree.filterTree(self.subreddit.name,"Post whitelist",filterContent,curses.COLS,config.fancy_characters,True)
    def treeBP(self,filterContent):
        return tree.filterTree(self.subreddit.name,"Post blacklist",filterContent,curses.COLS,config.fancy_characters,True)