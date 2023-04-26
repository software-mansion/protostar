use serde::Serde;
use array::ArrayTrait;
use array::SpanTrait;

#[contract]
mod MinimalContract {
    use serde::Serde;
    use array::ArrayTrait;
    use array::SpanTrait;

    #[derive(Drop, Copy)]
    struct CustomStruct {
        a: felt252,
        b: felt252,
    }
    impl CustomStructSerde of Serde::<CustomStruct>{
          fn serialize(ref output: array::Array<felt252>, input: CustomStruct) {
            output.append(input.a);
            output.append(input.b);
          }
          fn deserialize(ref serialized: array::Span<felt252>) -> Option<CustomStruct> {
              Option::Some(CustomStruct {
                  a: *serialized.at(0_u32),
                  b: *serialized.at(1_u32)
              })
          }
    }

    #[constructor]
    fn constructor(custom_struct: CustomStruct) {
        assert(custom_struct.a != custom_struct.b, 'A=B')
    }

    #[external]
    fn empty() {}
}
