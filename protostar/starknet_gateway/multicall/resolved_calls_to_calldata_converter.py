from .multicall_protocols import ResolvedCall


class ResolvedCallsToCalldataConverter:
    def convert(self, resolved_calls: list[ResolvedCall]) -> list[int]:
        return []
