import pytest
import os
import sys

# Füge Projekt-Root zum Python-Path hinzu
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """Globales Test-Setup"""
    os.environ["TESTING"] = "true"
    yield
    del os.environ["TESTING"]