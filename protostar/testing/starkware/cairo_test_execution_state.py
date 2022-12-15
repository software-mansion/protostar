from dataclasses import dataclass

from protostar.testing.stopwatch import Stopwatch
from protostar.testing.test_output_recorder import OutputRecorder


@dataclass
class CairoTestExecutionState:
    # TODO: Should be extended with state of VM
    output_recorder: OutputRecorder
    stopwatch: Stopwatch

    def __init__(self):
        self.output_recorder = OutputRecorder()
        self.stopwatch = Stopwatch()
