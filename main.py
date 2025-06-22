from escpos.printer import Usb

import configparser
from modules.header import ModuleHeader
from modules.ticktick import ModuleTickTick



modules = []

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    modules.append(ModuleHeader())
    modules.append(ModuleTickTick(config['TickTick']))
    p = Usb(0x04b8, 0x0202)

    for module in modules:
        module.reciept_print(p)

    p.cut()

if __name__ == "__main__":
    main()
