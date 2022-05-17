import functools
import inspect
import sys


def replace_class(full_path: str, new_module):
    def replace_class_instance(func):
        @functools.wraps(func)
        async def with_replaced_class(*args, **kwargs):
            class_name = full_path.split(".")[-1]
            module_name = ".".join(full_path.split(".")[:-1])
            replaced_class = getattr(sys.modules[module_name], class_name)
            setattr(sys.modules[module_name], class_name, new_module)

            try:
                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
            finally:
                setattr(sys.modules[module_name], class_name, replaced_class)

            return result

        return with_replaced_class

    return replace_class_instance
