%lang starknet

from mock_util import addition
from mock_library.mock_source import THREE

@view
func add_3(a: felt) -> (res: felt):
    return addition(a, THREE)
end