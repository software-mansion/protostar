from dataclasses import dataclass
from typing import Optional


@dataclass
class NetworkConfig:
    starkware_network_name: Optional[str] = None
    gateway_url: Optional[str] = None
