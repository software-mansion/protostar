from typing import Literal

from ..network_config import PredefinedNetwork
from .block_explorer import BlockExplorer
from .stark_scan_block_explorer import StarkScanBlockExplorer
from .viewblock_block_explorer import ViewblockBlockExplorer
from .voyager_block_explorer import VoyagerBlockExplorer

SupportedBlockExplorerName = Literal["starkscan", "viewblock", "voyager"]


def create_block_explorer(
    block_explorer_name: SupportedBlockExplorerName, network: PredefinedNetwork
) -> BlockExplorer:
    if block_explorer_name == "viewblock":
        return ViewblockBlockExplorer(network)
    if block_explorer_name == "voyager":
        return VoyagerBlockExplorer(network)
    if block_explorer_name == "starkscan":
        return StarkScanBlockExplorer(network)
    assert False, f"Unknown block explorer: {block_explorer_name}"
