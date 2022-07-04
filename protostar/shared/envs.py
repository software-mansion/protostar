import os
from dataclasses import dataclass


@dataclass
class ProtostarEnvs:
    protostar_dev: bool


protostar_envs = ProtostarEnvs(protostar_dev="PROTOSTAR_DEV" in os.environ)
