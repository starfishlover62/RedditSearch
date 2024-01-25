class Text:
    def __init__(self,contents):
        self.updateContents(contents)

    def updateContents(self,contents):
        self.contents = contents



class Line:
    content = ""
    displayContent = ""
    justify = 0 # 0 - Left, 1 - Center, 2 - Right
    width = 80
    def __init__(self,content,width = 80):
        self.updateContent(content,width)

    def updateContent(self,content,width = 80):
        if(len(content) <= width):
            self.content = content
            self.width = width
            self.displayContent = self.content
            return True
        else:
            return False
    
    def returnLine(self):
        return self.displayContent

    def justifyLeft(self):
        self.justify = 0
        self.displayContent = self._placeString(self.content,self.width)
    
    def justifyCenter(self):
        self.justify = 1
        frontMargin = int((self.width - len(self.content))/2) # Number of leading spaces before content
        self.displayContent = self._placeString(self.content,self.width,frontMargin)

    def justifyRight(self):
        self.justify = 2
        frontMargin = self.width - len(self.content) # Number of leading spaces before content
        self.displayContent = self._placeString(self.content,self.width,frontMargin)

    def _placeString(self,string,length,start=0):
        if(len(string)>=length):
            return string
        s = ""
        s = s.zfill(length)
        s = s.replace("0"," ")
        s = s[:start] + string + s[start+len(string):]
        return s