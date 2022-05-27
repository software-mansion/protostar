from types import SimpleNamespace


class TmpState(SimpleNamespace):
    SUPPORTED_TYPES = (int, str, bool)

    def validate(self) -> bool:
        for key in vars(self):
            val = getattr(self, key)
            if not isinstance(val, TmpState.SUPPORTED_TYPES):
                return False
        return True
