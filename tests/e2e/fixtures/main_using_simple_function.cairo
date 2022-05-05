%lang starknet
from my_lib.utils import get_my_number

@view
func my_func() -> (res : felt):
    let (res) = get_my_number()
    return (res)
end
