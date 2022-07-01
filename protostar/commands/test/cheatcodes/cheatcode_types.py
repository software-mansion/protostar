from typing import Dict, List, Union

from protostar.utils.data_transformer_facade import DataTransformerFacade


CairoArguments = Union[
                    List[int],
                    Dict[
                        DataTransformerFacade.ArgumentName,
                        DataTransformerFacade.SupportedType,
                    ],
                ]