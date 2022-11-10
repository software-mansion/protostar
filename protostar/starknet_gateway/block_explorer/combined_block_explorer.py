from typing import Callable, Optional

from protostar.io.log_color_provider import log_color_provider

from .block_explorer import BlockExplorer, ClassHash, ContractAddress, TransactionHash


class CombinedBlockExplorer(BlockExplorer):
    def __init__(self, block_explorers: list[BlockExplorer]) -> None:
        self._block_explorers = block_explorers

    def get_name(self) -> str:
        return "+".join([explorer.get_name() for explorer in self._block_explorers])

    def create_link_to_class(self, class_hash: ClassHash) -> Optional[str]:
        return self._aggregate_links(
            on_picking_link=lambda explorer: explorer.create_link_to_class(class_hash)
        )

    def create_link_to_contract(
        self, contract_address: ContractAddress
    ) -> Optional[str]:
        return self._aggregate_links(
            on_picking_link=lambda explorer: explorer.create_link_to_contract(
                contract_address
            )
        )

    def create_link_to_transaction(self, tx_hash: TransactionHash) -> Optional[str]:
        return self._aggregate_links(
            on_picking_link=lambda explorer: explorer.create_link_to_transaction(
                tx_hash
            )
        )

    def _aggregate_links(
        self, on_picking_link: Callable[[BlockExplorer], Optional[str]]
    ):
        longest_name = len(
            max((explorer.get_name() for explorer in self._block_explorers), key=len)
        )

        def format_name(name: str) -> str:
            result = name.ljust(longest_name, " ")
            result = log_color_provider.bold(result)
            return log_color_provider.colorize("MAGENTA", content=result)

        return "\n".join(
            [
                f"{format_name(explorer.get_name())} {on_picking_link(explorer) or '—'}"
                for explorer in self._block_explorers
            ]
        )
