class ProtostarException(Exception):
    # Disabling pylint to narrow down types
    # pylint: disable=useless-super-delegation
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
