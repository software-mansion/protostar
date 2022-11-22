import requests

from protostar.starknet_gateway import Wei
from protostar.starknet import Address


class FaucetContract:
    """Contract for prefunding deployments"""

    def __init__(self, devnet_gateway_url: str) -> None:
        self._devnet_gateway_url = devnet_gateway_url

    async def transfer(self, recipient: Address, amount: Wei):
        requests.post(
            url=f"{self._devnet_gateway_url}/mint",
            json={
                "address": str(recipient),
                "amount": amount,
                "lite": True,
            },
            timeout=10,
        )
