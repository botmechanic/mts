# test_agent.py
from pydantic_ai import Agent
import inspect

# Print Agent class signature
print("Agent signature:")
print(inspect.signature(Agent.__init__))

# Print available attributes and methods
print("\nAgent attributes and methods:")
print(dir(Agent))

# Try to get help documentation
print("\nAgent documentation:")
print(Agent.__doc__)