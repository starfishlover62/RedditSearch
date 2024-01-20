import curses
from formatString import placeString
class ScrollingList:
    """Represents a list that can be scrolled through. Useful for displaying a large amount of related data.
     Requires a list of strings, a curses window object, and optionally a starting line number and/or a 
     ToolTip object.
    """
    def __init__(self, screen, stringList, line = 0, tooltip = None):
        self.updateStrings(screen,stringList,line,tooltip)
    
    def updateStrings(self,screen,stringList,line = 0, tooltip = None):
        self.screen = screen
        self.lines = stringList
        self.currentLine = line
        self.tooltip = tooltip
        self.maxLine = curses.LINES
        if(not self.tooltip == None):
            self.maxLine -= self.tooltip.height()
        
        self.maxLine = len(self.lines) - self.maxLine
    
    def scrollDown(self, numLines = 1):
        """Moves the lines that will be shown down by numLines.
         Returns the current line number
        """
        if(self.currentLine + numLines > self.maxLine):
            self.currentLine = self.maxLine
        else:
            self.currentLine += numLines
        return self.currentLine
        
    
    def scrollUp(self, numLines = 1):
        if(self.currentLine - numLines < 0):
            self.currentLine = 0
        else:
            self.currentLine = self.currentLine - numLines
        return self.currentLine
    
    def getLines(self):
        lines = []
        if(not self.tooltip == None):
            numLines = curses.LINES - self.tooltip.height()
            lines = self.lines[self.currentLine:self.currentLine+numLines]
            while(len(lines) < numLines):
                lines.append("")
            lines = lines + self.tooltip.lines
            if((len(lines) == curses.LINES) and (len(lines[-1]) >= curses.COLS)):
                lines[-1] = lines[-1][:-1]
        else:
            numLines = curses.LINES
            lines = self.lines[self.currentLine:self.currentLine+numLines]
            while(len(lines) < numLines):
                lines.append("")
            if((len(lines) == curses.LINES) and (len(lines[-1]) >= curses.COLS)):
                lines[-1] = lines[-1][:-1]
        return lines

    def updateTooltip(self,tooltip):
        if(not tooltip == None):
            self.tooltip = tooltip
            self.maxLine -= self.tooltip.height()
        


class ToolTip:
    """ Represents the tooltip that is anchored to the bottom of a scrolling list. Items will be displayed
     in the order that they are added. Those added first will be above those added later
    """
    def __init__(self,lines):
        self.replace(lines)

    def replace(self,lines):
        self.lines = []
        if(type(lines) == str):
            self.lines.append(lines)
        elif(type(lines) == list):
            for item in lines:
                self.lines.append(item)

    def height(self):
        return len(self.lines)