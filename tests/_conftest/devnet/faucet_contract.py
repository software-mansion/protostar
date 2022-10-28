from starknet_py.constants import DEVNET_FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.net import AccountClient

from protostar.starknet_gateway import Wei


class FaucetContract:
    """Contract for prefunding deployments"""

    def __init__(self, predeployed_account_client: AccountClient) -> None:
        self._predeployed_account_client = predeployed_account_client

    async def transfer(self, recipient: int, amount: Wei):
        fee_contract = Contract(
            address=DEVNET_FEE_CONTRACT_ADDRESS,
            abi=self._get_abi(),
            client=self._predeployed_account_client,
        )

        res = await fee_contract.functions["transfer"].invoke(
            recipient=recipient, amount=amount, max_fee=int(1e20)
        )
        await res.wait_for_acceptance()

    def _get_abi(self):
        return [
            {
                "inputs": [
                    {"name": "recipient", "type": "felt"},
                    {"name": "amount", "type": "Uint256"},
                ],
                "name": "transfer",
                "outputs": [{"name": "success", "type": "felt"}],
                "type": "function",
            },
            {
                "members": [
                    {"name": "low", "offset": 0, "type": "felt"},
                    {"name": "high", "offset": 1, "type": "felt"},
                ],
                "name": "Uint256",
                "size": 2,
                "type": "struct",
            },
        ]
