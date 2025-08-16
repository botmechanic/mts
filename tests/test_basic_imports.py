
import pytest

def test_mts_import():
    try:
        import mts
        assert True
    except ImportError:
        pytest.fail("Failed to import 'mts' module.")

def test_mts_core_config_import():
    try:
        from mts.core import config
        assert True
    except ImportError:
        pytest.fail("Failed to import 'mts.core.config' module.")

def test_mts_adk_agents_import():
    try:
        from mts import adk_agents
        assert True
    except ImportError:
        pytest.fail("Failed to import 'mts.adk_agents' module.")

def test_mts_adk_tools_import():
    try:
        from mts import adk_tools
        assert True
    except ImportError:
        pytest.fail("Failed to import 'mts.adk_tools' module.")

def test_mts_orchestrator_import():
    try:
        from mts.orchestrator import MTSOrchestrator
        assert True
    except ImportError:
        pytest.fail("Failed to import 'mts.orchestrator' module.")
