# pylint: disable=invalid-name
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from protostar.commands.test import TestCommand
from protostar.utils.compiler.protostar_preprocessor import get_protostar_pass_manager
from protostar.utils.starknet_compilation import StarknetCompiler
from tests.integration.conftest import assert_cairo_test_cases


async def test_protostar_pass(mocker: MockerFixture):
        compiler = StarknetCompiler(
            include_paths=[],
            disable_hint_validation = True,
            custom_pass_manager_factory = get_protostar_pass_manager
        )

        contract_class = compiler.compile_contract(Path(__file__).parent / "contract.cairo")
        
        first_type = {'name': 'Key', 'type': 'struct', 'members': [{'name': 'a', 'type': 'felt', 'offset': 0}, {'name': 'b', 'type': 'felt', 'offset': 1}], 'size': 2} 
        second_type = {'name': 'Value', 'type': 'struct', 'members': [{'name': 'a', 'type': 'felt', 'offset': 0}, {'name': 'b', 'type': 'felt', 'offset': 1}], 'size': 2}
        assert first_type in contract_class.abi
        assert second_type in contract_class.abi
