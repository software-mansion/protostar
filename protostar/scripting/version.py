from protostar.scripting_runtime.api_context import api_context

__all__ = ("__version__",)

__version__: str = api_context().protostar_version
