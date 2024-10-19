import curses

from formatString import combineStrings


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
    
    def scrollBottom(self):
        self.currentLine = self.maxLine
        return self.currentLine

    def scrollUp(self, numLines=1):
        if self.currentLine - numLines < 0:
            self.currentLine = 0
        else:
            self.currentLine = self.currentLine - numLines
        return self.currentLine
    
    def scrollTop(self):
        self.currentLine = 0
        return self.currentLine

    def getLines(self):
        lines = []
        if self.tooltip is not None:
            numLines = curses.LINES - self.tooltip.height()
            lines = self.lines[self.currentLine : self.currentLine + numLines]
            while len(lines) < numLines:
                lines.append("")
            for item in self.tooltip.lines:
                lines = lines + [item.string]
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
            self.lines.append(Line(lines, 0))
        elif isinstance(lines, list):
            for item in lines:
                if isinstance(item, str):
                    self.lines.append(Line(item, 0))
                elif isinstance(item, Line):
                    self.lines.append(item)
        self.format = self.lines

    def update(self, lines, index=0):
        temp = self.lines
        try:
            if isinstance(lines, str):  # Converts a string to a single element list
                lines = [Line(lines, 0)]
            if isinstance(
                lines, list
            ):  # Loops through each item in list, replacing elements in self.lines with them
                for item in lines:  # Starts at index, and replaces elements until the end of lines has been reached
                    if isinstance(item, str):
                        self.lines[index] = Line(item, 0)
                    elif isinstance(item, Line):
                        self.lines[index] = item
                    index = index + 1
        except (
            IndexError
        ):  # If lines was too long, reset self.lines back to its original value
            self.lines = temp

        self.format = self.lines

    def updateVars(self, values, index=0):
        if values is not None:
            if index < len(self.lines):
                self.lines[index].updateVars(values)

    def height(self):
        return len(self.lines)


class Line:
    def __init__(self, sections, positions, length=80):
        self.string = ""
        self.sections = []
        self.positions = []
        self.length = 0
        self.format = []
        
        self.replace(sections, positions, length)

    def replace(self, sections, positions, length=80):
        if sections is not None and positions is not None:
            if isinstance(sections, str):
                sections = [sections]
            if isinstance(sections, list):
                if isinstance(positions, int):
                    positions = [positions]
                if isinstance(positions, list):
                    if len(sections) == len(positions):
                        self.sections = list(sections)
                        self.format = sections
                        self.positions = positions
                        self.length = length
                        for index in range(len(sections)):
                            self.string = combineStrings(
                                self.string,
                                sections[index],
                                length,
                                0,
                                positions[index],
                            )
                        self.previousValues = None

    def place(self):
        self.string = ""
        for index in range(len(self.sections)):
            self.string = combineStrings(
                self.string, self.sections[index], self.length, 0, self.positions[index]
            )

    def updateVars(self, values):
        if values is not None and self.previousValues != values:
            lines = []
            valIndex = 0
            index = 0
            if not isinstance(values, list):
                values = [values]
            for section in range(len(self.format)):
                text = self.format[section]
                while True:
                    if valIndex >= len(values):
                        break
                    index = text.find("%i")
                    if index == -1:
                        break
                    text = f"{text[:index]}{values[valIndex]}{text[index+2:]}"
                    valIndex = valIndex + 1
                lines.append(text)
            self.sections = lines
            self.place()
            self.previousValues = values
