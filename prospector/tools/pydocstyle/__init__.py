from pydocstyle.checker import AllError, ConventionChecker

from prospector.encoding import CouldNotHandleEncoding, read_py_file
from prospector.message import Location, Message, make_tool_error_message
from prospector.tools.base import ToolBase

__all__ = ("PydocstyleTool",)


class PydocstyleTool(ToolBase):
    def __init__(self, *args, **kwargs):
        super(PydocstyleTool, self).__init__(*args, **kwargs)
        self._code_files = []
        self.ignore_codes = ()

    def configure(self, prospector_config, found_files):
        self.ignore_codes = prospector_config.get_disabled_messages("pydocstyle")

    def run(self, found_files):
        messages = []

        checker = ConventionChecker()

        for code_file in found_files.iter_module_paths():
            try:
                for error in checker.check_source(read_py_file(code_file), code_file, None):

                    location = Location(
                        path=code_file,
                        module=None,
                        function="",
                        line=error.line,
                        character=0,
                        absolute_path=True,
                    )
                    message = Message(
                        # TODO: legacy naming for now
                        source="pydocstyle",
                        code=error.code,
                        location=location,
                        message=error.message.partition(":")[2].strip(),
                    )
                    messages.append(message)
            except CouldNotHandleEncoding as err:
                messages.append(
                    make_tool_error_message(
                        code_file,
                        "pydocstyle",
                        "D000",
                        message="Could not handle the encoding of this file: %s" % err.encoding,
                    )
                )
                continue
            except AllError as exc:
                # pydocstyle's Parser.parse_all method raises AllError when an
                # attempt to analyze the __all__ definition has failed.  This
                # occurs when __all__ is too complex to be parsed.
                messages.append(
                    make_tool_error_message(
                        code_file,
                        "pydocstyle",
                        "D000",
                        line=1,
                        character=0,
                        message=exc.args[0],
                    )
                )
                continue

        return self.filter_messages(messages)

    def filter_messages(self, messages):
        return [message for message in messages if message.code not in self.ignore_codes]