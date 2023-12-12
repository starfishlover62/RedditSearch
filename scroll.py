import curses
from formatString import placeString
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
        index = -1
        sharedRow = False
        if(len(self.rows) == 0):
            self.rows.append(row)
        else:
            for item in self.rows:
                if(item.y == row.y):
                    if(row.x < item.x):
                        item.string = row.string[:row.x + len(row.content)] + item.string[row.x + len(row.content):]
                    else:
                        item.string = item.string[:row.x] + row.string[row.x:row.x+len(row.content)] + item.string[row.x+len(row.content):]
                    sharedRow = True
                    break
                elif (item.y > row.y):
                    if(index == -1):
                        index = 1
                    else:
                        index = index +1
                
                    
            if(not sharedRow):
                if(not index == -1):
                    self.rows.insert(index,row)
                else:
                    self.rows.append(row)

        
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
    def __init__(self, y, x, string,length=80):
        self.y = y
        self.x = x
        self.content = string
        self.string = placeString(string,length,self.x)
    
