from protostar.starknet.data_transformer import CairoData
from protostar.cairo.short_string import short_string_to_str


def protostar_print(data: CairoData):
    for data_item in data:
        str_data = short_string_to_str(data_item)
        original_value_msg = f"original value: [{str(data_item)}]"
        converted_value_msg = f"converted to a string: [{str_data}]"
        print(original_value_msg, converted_value_msg)
