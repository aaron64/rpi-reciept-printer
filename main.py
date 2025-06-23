from escpos.printer import Usb

import configparser

from modules.header import ModuleHeader
from modules.ticktick import ModuleTickTick
from modules.weather import ModuleWeather

from RecieptPrinter import RecieptPrinter


modules = []
module_classes = [ModuleHeader, ModuleWeather, ModuleTickTick]

def main():
    p = RecieptPrinter(False)
    config = configparser.ConfigParser()
    config.read('config.ini')

    for ModuleClass in module_classes:
        module_config = config[ModuleClass.__name__] if ModuleClass.__name__ in config else None
        modules.append(ModuleClass(module_config))

    for module in modules:
        module.reciept_print(p)

    p.cut()

if __name__ == "__main__":
    main()
