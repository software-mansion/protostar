from .voyager_block_explorer import VoyagerBlockExplorer


def test_creating_link_to_transaction():
    explorer = VoyagerBlockExplorer(network="mainnet")

    link = explorer.create_link_to_transaction(123)

    assert link
