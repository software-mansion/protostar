from dataclasses import dataclass, field


from starknet_py.net.models.transaction import DeployAccount, Invoke, Transaction


@dataclass
class TransactionRegistry:
    invoke_txs: list[Invoke] = field(default_factory=list)
    deploy_account_txs: list[DeployAccount] = field(default_factory=list)

    def register(self, tx: Transaction):
        if isinstance(tx, Invoke):
            self.invoke_txs.append(tx)
        if isinstance(tx, DeployAccount):
            self.deploy_account_txs.append(tx)
