from pathlib import Path

def create_project_structure():
    """Create the MTS project directory structure."""
    # Define the base directories
    base_dirs = [
        "src/mts/agents",
        "src/mts/models",
        "src/mts/core",
        "src/mts/api/routes",
        "src/mts/services",
        "src/mts/utils",
        "tests/agents",
        "tests/models",
        "tests/api",
        "tests/services",
    ]
    
    # Define files to create
    python_files = {
        "src/mts/agents": ["__init__.py", "tank.py", "morpheus.py", "neo.py", "trinity.py", "oracle.py"],
        "src/mts/models": ["__init__.py", "system.py", "risk.py", "patterns.py", "execution.py", "market.py"],
        "src/mts/core": ["__init__.py", "config.py", "constants.py", "logging.py", "errors.py"],
        "src/mts/api": ["__init__.py", "deps.py"],
        "src/mts/api/routes": ["__init__.py", "agents.py", "trading.py", "system.py"],
        "src/mts/services": ["__init__.py", "hyperliquid.py", "claude.py"],
        "src/mts/utils": ["__init__.py", "metrics.py", "validation.py"],
        "tests": ["__init__.py"],
        "tests/agents": ["__init__.py"],
        "tests/models": ["__init__.py"],
        "tests/api": ["__init__.py"],
        "tests/services": ["__init__.py"],
    }
    
    # Create directories
    for dir_path in base_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create Python files
    for dir_path, files in python_files.items():
        for file_name in files:
            file_path = Path(dir_path) / file_name
            file_path.touch(exist_ok=True)
            
    # Create main application file
    Path("src/mts/main.py").touch(exist_ok=True)
    
    print("Project structure created successfully!")

if __name__ == "__main__":
    create_project_structure()