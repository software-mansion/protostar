from protostar.commands.test.cheatcodes.cheatcode import Cheatcode


class DeployContract(Cheatcode):
    @staticmethod
    def name() -> str:
        return "deploy"

    def build(self):
        assert False, "Not implemented"
