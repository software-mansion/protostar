from dataclasses import dataclass, field


@dataclass
class RunsCounter:
    """
    A boxed integer that can be safely shared between Python threads.
    It is used to count fuzz test runs.
    """

    budget: int
    count: int = field(default=0)

    def __next__(self) -> int:
        self.count += 1
        return self.count

    @property
    def balance(self) -> int:
        return self.budget - self.count

    @property
    def available_runs(self) -> int:
        return max(0, self.balance)
