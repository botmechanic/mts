# test_models.py
from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName

# Try to print available models
print("Known models:")
try:
    print(KnownModelName.__args__)
except AttributeError:
    print("Could not get models directly")

# Try creating an agent with different models
models_to_test = [
    "openai:gpt-4",
    "openai:gpt-3.5-turbo",
    "anthropic:claude-2",
    "anthropic:claude-3"
]

for model in models_to_test:
    try:
        agent = Agent(model=model)
        print(f"Success: {model}")
    except Exception as e:
        print(f"Failed: {model} - {str(e)}")