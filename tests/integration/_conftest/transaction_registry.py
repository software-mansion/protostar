from dataclasses import dataclass, field

from starknet_py.net.client_models import InvokeFunction, StarknetTransaction
from starknet_py.net.models.transaction import DeployAccount


@dataclass
class TransactionRegistry:
    invoke_txs: list[InvokeFunction] = field(default_factory=list)
    deploy_account_txs: list[DeployAccount] = field(default_factory=list)

    def register(self, tx: StarknetTransaction):
        if isinstance(tx, InvokeFunction):
            self.invoke_txs.append(tx)
        if isinstance(tx, DeployAccount):
            self.deploy_account_txs.append(tx)
