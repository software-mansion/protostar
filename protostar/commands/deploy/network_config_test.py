from typing import Optional

import pytest
from pytest_mock import MockerFixture

from protostar.commands.deploy.network_config import (
    InvalidNetworkConfigException,
    NetworkConfig,
)


@pytest.fixture(name="network")
def network_fixture() -> Optional[str]:
    return None


@pytest.fixture(name="gateway_url")
def gateway_url_fixture() -> Optional[str]:
    return None


@pytest.fixture(name="project")
def project_fixture(mocker: MockerFixture, network, gateway_url):
    project_mock = mocker.MagicMock()

    def load_argument(_, attr_name: str):
        if attr_name == "gateway_url":
            return gateway_url
        if attr_name == "network":
            return network
        assert False

    project_mock.load_argument = load_argument
    return project_mock


def test_loading_starkware_networks():
    assert NetworkConfig.from_starkware_network("alpha-goerli").gateway_url is not None
    assert NetworkConfig.from_starkware_network("alpha-mainnet").gateway_url is not None


@pytest.mark.parametrize("gateway_url", ["http://localhost:5432/"])
def test_loading_gateway_from_config_file(project):
    network_config = NetworkConfig.from_config_file("_", project)

    assert network_config.gateway_url == "http://localhost:5432/"


@pytest.mark.parametrize("network", ["alpha-goerli"])
def test_loading_gateway_based_on_network_from_config_file(project):
    network_config = NetworkConfig.from_config_file("_", project)

    assert network_config.gateway_url is not None


def test_error_on_invalid_network_configuration(project):
    with pytest.raises(InvalidNetworkConfigException):
        NetworkConfig.from_config_file("_", project)
