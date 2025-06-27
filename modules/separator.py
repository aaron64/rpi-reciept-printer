from RecieptPrinter import CHAR_WIDTH
DEFAULT_SEPARATOR = "-"

class ModuleSeparator:
    def __init__(self, config):
        self.pattern = config['pattern'] if 'pattern' in config else DEFAULT_SEPARATOR
        self.size = int(42/len(self.pattern))

    def reciept_print(self, p):
        p.text(self.pattern * self.size)
