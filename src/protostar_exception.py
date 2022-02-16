class ProtostarException(Exception):
    # Disabling pylint to narrow down types
    # pylint: disable=useless-super-delegation
    def __init__(self, message: str, should_append_link_to_report_page: bool = False):
        self.message = message
        if should_append_link_to_report_page:
            self.message += "\nReport the issue here: https://github.com/software-mansion/protostar/issues"
        super().__init__(message)
