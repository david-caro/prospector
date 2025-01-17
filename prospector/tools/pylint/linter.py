from pylint import version as pylint_version
from pylint.lint import PyLinter
from pylint.utils import _splitstrip


class ProspectorLinter(PyLinter):
    def __init__(self, found_files, *args, **kwargs):
        self._files = found_files
        # set up the standard PyLint linter
        PyLinter.__init__(self, *args, **kwargs)

    def config_from_file(self, config_file=None):
        """Will return `True` if plugins have been loaded. For pylint>=1.5. Else `False`."""
        self.read_config_file(config_file)
        if self.cfgfile_parser.has_option("MASTER", "load-plugins"):
            plugins = _splitstrip(self.cfgfile_parser.get("MASTER", "load-plugins"))
            self.load_plugin_modules(plugins)
        self.load_config_file()
        return True

    def _expand_files(self, modules):
        expanded = super()._expand_files(modules)
        # PyLinter._expand_files returns dict since 2.15.7.
        if pylint_version > "2.15.6":
            filtered = {}
            for module in expanded:
                if self._files.check_module(module):
                    filtered[module] = expanded[module]
        else:
            filtered = []
            for module in expanded:
                if self._files.check_module(module["path"]):
                    filtered.append(module)
        return filtered
