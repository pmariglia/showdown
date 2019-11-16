# import all modules in this package
# ref: https://stackoverflow.com/questions/1057431/how-to-load-all-modules-in-a-folder

from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
