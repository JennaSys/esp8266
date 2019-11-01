import sys

# Use to remove an already imported module allowing it to be reloaded
#   NOTE: It doesn't remove it from the namespace!
def unload(module_name):
    if len(module_name) > 0:
        del sys.modules[module_name]