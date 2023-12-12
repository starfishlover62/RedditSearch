import curses
class ScrollingList:
    def __init__(self, screen, stringList, line = 0, tooltip = None):
        self.screen = screen
        self.lines = stringList
        self.currentLine = line
        self.tooltip = tooltip
        self.maxLine = curses.LINES
        print(self.maxLine)
        if(not self.tooltip == None):
            self.maxLine -= self.tooltip.height()
        
        print(f"{len(self.lines)} - {self.maxLine}")
        self.maxLine = len(self.lines) - self.maxLine
        print(self.maxLine)
    
    def scrollDown(self, numLines = 1):
        if(self.currentLine + numLines > self.maxLine):
            self.currentLine = self.maxLine
        else:
            self.currentLine += numLines
        
    
    def scrollUp(self, numLines = 1):
        if(self.currentLine - numLines < 0):
            self.currentLine = 0
        else:
            self.currentLine = self.currentLine - numLines
    
    def getLines(self):
        numLines = curses.LINES - self.tooltip.height()
        return self.lines[self.currentLine:self.currentLine+numLines] + self.tooltip.returnLines()
        


class ToolTip:
    def __init__(self,rows):
        self.rows = []
        for item in rows:
            self.addRow(item)
    
    def addRow(self, row):
        self.rows.append(row)
        index = 0
        for item in self.rows:
            if (item.y > row.y):
                temp = item
                self.rows[index] = self.rows[-1]
                self.rows[-1] = temp
                break
            index = index +1
        
    def returnRows(self):
        return self.rows

    def returnLines(self):
        ls = []
        for item in self.rows:
            ls.append(item.string)
        
        return ls

    def height(self):
        return len(self.rows)

class Row:
    def __init__(self, y, x, string):
        self.y = y
        self.x = x
        self.string = string
    
