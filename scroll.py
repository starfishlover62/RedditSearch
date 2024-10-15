import curses


# from formatString import placeString
class ScrollingList:
    """Represents a list that can be scrolled through. Useful for displaying a large amount of related data.
    Requires a list of strings, a curses window object, and optionally a starting line number and/or a
    ToolTip object.
    """

    def __init__(self, screen, stringList, line=0, tooltip=None):
        self.updateStrings(screen, stringList, line, tooltip)

    def updateStrings(self, screen, stringList, line=0, tooltip=None):
        self.screen = screen
        self.lines = stringList
        self.currentLine = line
        self.updateTooltip(tooltip)
        # self.tooltip = tooltip
        # self.maxLine = curses.LINES
        # if(not self.tooltip == None):
        #     self.maxLine -= self.tooltip.height()

        # self.maxLine = len(self.lines) - self.maxLine

    def scrollDown(self, numLines=1):
        """Moves the lines that will be shown down by numLines.
        Returns the current line number
        """
        if self.currentLine + numLines > self.maxLine:
            self.currentLine = self.maxLine
        else:
            self.currentLine += numLines
        return self.currentLine

    def scrollUp(self, numLines=1):
        if self.currentLine - numLines < 0:
            self.currentLine = 0
        else:
            self.currentLine = self.currentLine - numLines
        return self.currentLine

    def getLines(self):
        lines = []
        if self.tooltip is not None:
            numLines = curses.LINES - self.tooltip.height()
            lines = self.lines[self.currentLine : self.currentLine + numLines]
            while len(lines) < numLines:
                lines.append("")
            lines = lines + self.tooltip.lines
            if (len(lines) == curses.LINES) and (len(lines[-1]) >= curses.COLS):
                lines[-1] = lines[-1][:-1]
        else:
            numLines = curses.LINES
            lines = self.lines[self.currentLine : self.currentLine + numLines]
            while len(lines) < numLines:
                lines.append("")
            if (len(lines) == curses.LINES) and (len(lines[-1]) >= curses.COLS):
                lines[-1] = lines[-1][:-1]
        return lines

    def updateTooltip(self, tooltip):
        self.maxLine = curses.LINES
        self.tooltip = None
        if tooltip is not None:
            self.tooltip = tooltip
            self.maxLine -= (
                self.tooltip.height()
            )  # Applies line adjustment for new tooltip

        if len(self.lines) >= self.maxLine:
            self.maxLine = len(self.lines) - self.maxLine
        else:
            self.maxLine = 0

    def print(self, numLines=None):
        """
        Prints the values returned by getLines to the screen. Prints numLines number of lines if specified
        """
        if numLines is None or numLines > 0:
            ticker = 0
            self.screen.clear()
            for item in self.getLines():
                self.screen.addstr(ticker, 0, f"{item}")
                ticker = ticker + 1
                if numLines is not None and ticker >= numLines:
                    self.screen.refresh()
                    break
            self.screen.refresh()


class ToolTip:
    """Represents the tooltip that is anchored to the bottom of a scrolling list. Items will be displayed
    in the order that they are added. Those added first will be above those added later
    """

    def __init__(self, lines):
        self.replace(lines)

    def replace(self, lines):
        self.lines = []
        if isinstance(lines, str):
            self.lines.append(lines)
        elif isinstance(lines, list):
            for item in lines:
                self.lines.append(item)

    def update(self,lines,index=0):
        temp = self.lines
        try:
            if isinstance(lines,str): # Converts a string to a single element list
                lines = [lines]
            if isinstance(lines,list): # Loops through each item in list, replacing elements in self.lines with them
                for item in lines: # Starts at index, and replaces elements until the end of lines has been reached
                    self.lines[index] = item
                    index = index + 1
        except IndexError: # If lines was too long, reset self.lines back to its original value
            self.lines = temp
    
    
    def height(self):
        return len(self.lines)
