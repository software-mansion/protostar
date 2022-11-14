from typing import Literal, Optional

from ..network_config import PredefinedNetwork
from .block_explorer import BlockExplorer
from .stark_scan_block_explorer import StarkScanBlockExplorer
from .viewblock_block_explorer import ViewblockBlockExplorer
from .voyager_block_explorer import VoyagerBlockExplorer
from .fake_block_explorer import FakeBlockExplorer
from .combined_block_explorer import CombinedBlockExplorer

SupportedBlockExplorerName = Literal["starkscan", "viewblock", "voyager"]
SUPPORTED_BLOCK_EXPLORER_NAMES: list[SupportedBlockExplorerName] = [
    "starkscan",
    "viewblock",
    "voyager",
]


def create_block_explorer(
    block_explorer_name: Optional[SupportedBlockExplorerName],
    network: Optional[PredefinedNetwork],
) -> BlockExplorer:
    if network:
        if block_explorer_name is None:
            return CombinedBlockExplorer(
                [StarkScanBlockExplorer(network), VoyagerBlockExplorer(network)]
            )
        if block_explorer_name == "viewblock":
            return ViewblockBlockExplorer(network)
        if block_explorer_name == "voyager":
            return VoyagerBlockExplorer(network)
        if block_explorer_name == "starkscan":
            return StarkScanBlockExplorer(network)
    return FakeBlockExplorer()
