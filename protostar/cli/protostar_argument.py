from typing import Union

from .arg_type import ArgTypeName
from .argument import Argument
from .protostar_arg_type import CustomProtostarArgTypeName

ProtostarArgument = Argument[Union[ArgTypeName, CustomProtostarArgTypeName]]
