import pydantic_ai
print("Available in pydantic_ai:")
print(dir(pydantic_ai))

try:
    from pydantic_ai import models
    print("\nAvailable in models:")
    print(dir(models))
except ImportError as e:
    print("Couldn't import models:", e)