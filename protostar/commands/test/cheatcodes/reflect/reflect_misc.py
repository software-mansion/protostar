from typing import Union, NamedTuple, Dict, Any, Type, List, Tuple
from dataclasses import dataclass
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.cairo.lang.vm.vm_consts import VmConstsReference


@dataclass
class ReflectTreeNode:
    typename: str
    value: Union[Dict, int, str]


ReflectInputType = Union[VmConstsReference, RelocatableValue, None, int]
ReflectValueType = Union[ReflectTreeNode, RelocatableValue, int]
ReflectReturnType = Union[NamedTuple, RelocatableValue, None, int]


def isinstance_namedtuple(obj: Any) -> bool:
    return (
        isinstance(obj, tuple) and hasattr(obj, "_asdict") and hasattr(obj, "_fields")
    )


def traverse_pre_order(tree: ReflectTreeNode) -> List[ReflectValueType]:
    stack: List[ReflectValueType] = [tree]
    pre_order: List[ReflectValueType] = []

    while len(stack) > 0:
        curr = stack.pop()
        pre_order.append(curr)
        if isinstance(curr, ReflectTreeNode):
            assert isinstance(curr.value, dict)
            for _, node in curr.value.items():
                stack.append(node)

    return pre_order


def to_cairo_naming(input_type: Type):
    if input_type == RelocatableValue:
        return "pointer"
    if input_type == int:
        return "felt"
    if input_type == VmConstsReference:
        return "struct"
    assert False, "Not a valid cairo type"


# pylint: disable=C0103
def PrettyNamedTuple(name: str, tuple_args: List[Tuple[str, Type]]) -> Type:
    def new_str(self):
        stack: List[Tuple[Union[Any, RelocatableValue, str, int], int]] = [(self, 0)]
        result: List[str] = []
        depth = 0

        while len(stack) > 0:
            curr, depth = stack.pop()

            if not isinstance_namedtuple(curr):
                result.append(str(curr) + ("" if isinstance(curr, str) else "\n"))
            else:
                result.append(f"{type(curr).__name__}(\n")
                stack.append(("    " * depth + ")\n", 0))

                for name, child in reversed(list(curr._asdict().items())):  # type: ignore
                    stack.append((child, depth + 1))
                    stack.append(("    " * (depth + 1) + f"{name}=", 0))

        return "".join(result)

    tpl = NamedTuple(name, tuple_args)
    tpl.__str__ = new_str
    return tpl
