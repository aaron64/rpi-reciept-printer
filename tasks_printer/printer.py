import configparser

from .modules.header import ModuleHeader
from .modules.tasks import ModuleTickTick
from .modules.weather import ModuleWeather
from .modules.separator import ModuleSeparator
# from .modules.events import ModuleEvents

from RecieptPrinter import RecieptPrinter


module_classes = [ModuleHeader, ModuleWeather, ModuleSeparator, ModuleTickTick]

def run(dry, config_path="config.ini"):
    p = RecieptPrinter(dry)
    config = configparser.ConfigParser()
    config.read(config_path)

    print("Creating modules...")
    modules = []
    for ModuleClass in module_classes:
        module_config = config[ModuleClass.__name__] if ModuleClass.__name__ in config else {}
        modules.append(ModuleClass(module_config))

    print("Printing...")
    for module in modules:
        module.reciept_print(p)

    p.cut()

    ticktick_module = next(m for m in modules if isinstance(m, ModuleTickTick))
    return [task for project in ticktick_module.projects for task in project.tasks_today()]
