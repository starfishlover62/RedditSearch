import curses

from scroll import ScrollingList, ToolTip, Line

class Page:

    def __init__(self,screen=None,scrollingList=None,tooltip=None,tooltipTypes=None,onUpdate=None,content=None,minRows=24,minCols=80):
        self.update(screen=screen,scrollingList=scrollingList,tooltip=tooltip,tooltipTypes=tooltipTypes,onUpdate=onUpdate,content=content,minRows=minRows,minCols=minCols)

    def update(self,screen=None,scrollingList=None,tooltip=None,tooltipTypes=None,onUpdate=None,content=None,minRows=24,minCols=80):
        if isinstance(screen,curses.window):
            self.screen = screen
        else:
            self.screen = None

        if isinstance(scrollingList,ScrollingList):
            self.scrollingList = scrollingList
        else:
            self.scrollingList = None

        if isinstance(tooltip,ToolTip):
            self.tooltip = tooltip
        else:
            self.tooltip = None
        self.tooltipTypes = tooltipTypes
        self.tooltipType = None

        self.content = content
        self.onUpdate = onUpdate
        self.minRows = minRows
        self.minCols = minCols
    
    def updateContent(self,content=None):
        if content is not None:
            self.content = content
        self.scrollingList.updateStrings(self.screen,self.onUpdate(self.content),self.scrollingList.currentLine,self.tooltip)

    def resize(self):
        if self.onUpdate is not None and self.screen is not None and self.scrollingList is not None:
            size = list(self.screen.getmaxyx())
            if size[0] < self.minRows:
                size[0] = self.minRows
            if size[1] < self.minCols:
                size[1] = self.minCols
            curses.resize_term(size[0], size[1])

            newContent = self.onUpdate(self.content) # Gets the properly sized content

            self.scrollingList.updateStrings(
                self.screen, newContent, self.scrollingList.currentLine, self.tooltip
            )  # Adds the headers list to the pagination controller
            temp = self.scrollingList.currentLine
            lineNum = self.scrollingList.scrollDown()
            if not temp == lineNum:
                lineNum = self.scrollingList.scrollUp()

    def print(self,numLines=None):
        self.scrollingList.print(numLines)
    

    def switchTooltip(self,key):
        if self.tooltipType != key:
            try:
                text = self.tooltipTypes[key]
                self.tooltipType = key
                self.tooltip.replace(text)
            except KeyError:
                return
    
    def updateTooltip(self,vars,index=0):
        self.tooltip.updateVars(vars,index)
    
    def refreshTooltip(self,key,vars,index=0,print=False,numLines=None):
        self.switchTooltip(key)
        self.updateTooltip(vars,index)
        if print:
            self.print(numLines)
