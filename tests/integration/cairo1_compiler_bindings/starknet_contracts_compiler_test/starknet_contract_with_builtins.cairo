#[contract]
mod HelloStarknetBuiltins {
    extern type Bitwise;
    extern fn bitwise(a: u128, b: u128) -> (u128, u128, u128) implicits(Bitwise) nopanic;

    fn test_pedersen() -> felt {
        pedersen(pedersen(pedersen(1, 2), 3), 4)
    }

    fn main() -> felt implicits(RangeCheck, GasBuiltin, EcOp) {
        bitwise(1_u128, 1_u128);
        pedersen(1, 2);
        100
    }
}