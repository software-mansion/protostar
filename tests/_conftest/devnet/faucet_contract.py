import requests

from protostar.starknet_gateway import Wei


class FaucetContract:
    """Contract for prefunding deployments"""

    def __init__(self, devnet_gateway_url: str) -> None:
        self._devnet_gateway_url = devnet_gateway_url

    async def transfer(self, recipient: int, amount: Wei):
        requests.post(
            url=f"{self._devnet_gateway_url}/mint",
            json={
                "address": hex(recipient),
                "amount": amount,
                "lite": True,
            },
            timeout=10,
        )
