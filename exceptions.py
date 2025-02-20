class NoBindingError(Exception):
    def __init__(self,msg="No keybindings were specified"):
        self.msg = msg
    def __str__(self):
        return self.msg