%lang starknet

from utils import addition
from some_lib.constants import THREE

@view
func add_3(a: felt) -> (res: felt) {
    return addition(a, THREE);
}
