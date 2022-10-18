from ..network_config import SimpleNetwork
from .voyager_link_generator import VoyagerLinkGenerator


# @pytest.mark.parametrize()
def test_transaction_link():
    voyager_link_generator = VoyagerLinkGenerator("testnet")

    voyager_link_generator.get_transaction_url(999)
