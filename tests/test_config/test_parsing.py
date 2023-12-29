import pytest
from pathlib import Path
from satisfactory_tools.config import parse_config


def game_config_exists(game_config_path: str | Path="./Docs.json") -> bool:
    if not isinstance(game_config_path, Path):
        game_config_path = Path(game_config_path)

    return game_config_path.exists()

pytestmark = pytest.mark.skipif(not game_config_exists(), reason="Game config not at given path")

def test_parse_config():
    parse_config("./Docs.json")
