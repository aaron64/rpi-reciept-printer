from .modules.header import ModuleHeader
from .modules.tasks import ModuleTickTick
from .modules.weather import ModuleWeather
from .modules.separator import ModuleSeparator
from .modules.workout import ModuleWorkout

module_classes = [ModuleHeader, ModuleWeather, ModuleSeparator, ModuleTickTick, ModuleWorkout]


def render_receipt(p, context, config):
    for ModuleClass in module_classes:
        module_config = config[ModuleClass.__name__] if ModuleClass.__name__ in config else {}
        module = ModuleClass(module_config)
        module.render(p, context)
