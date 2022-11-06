from dataclasses import dataclass
from typing import Optional, Sequence

DottedPath = str
Identifier = str


class Construct:
    pass


@dataclass
class FromImportConstruct(Construct):
    dotted_path: DottedPath
    imports: Sequence[str]


@dataclass
class ClassAttributeConstruct(Construct):
    name: str
    type_name: str
    default: Optional[str] = None


@dataclass
class DataclassConstruct(Construct):
    name: str
    class_attributes: Sequence[ClassAttributeConstruct]


@dataclass
class ModuleConstruct(Construct):
    imports: Sequence[FromImportConstruct]
    children: Sequence[DataclassConstruct]
