from protostar.starknet.data_transformer import CairoData
from protostar.cairo.short_string import short_string_to_str, is_short_string


def protostar_print(data: CairoData):
    for data_item in data:
        converted_value_msg = ""

        if is_short_string(data_item):
            str_data = short_string_to_str(data_item)
            converted_value_msg = f"converted to a string: [{str_data}]"

        original_value_msg = f"original value: [{str(data_item)}]"
        print(original_value_msg, converted_value_msg)
