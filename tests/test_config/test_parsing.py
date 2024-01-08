import pytest
from pathlib import Path
from satisfactory_tools.config.parser import ConfigParser
import json


def game_config_exists(game_config_path: str | Path="./Docs.json") -> bool:
    if not isinstance(game_config_path, Path):
        game_config_path = Path(game_config_path)

    return game_config_path.exists()

pytestmark = pytest.mark.skipif(not game_config_exists(), reason="Game config not at given path")

def test_ConfigParser():
    parser = ConfigParser(Path("./Docs.json"))
    config = parser.parse_config()
    breakpoint()


def test_simplify_config():
    config_content = json.loads(Path("./Docs.json").read_text(encoding="utf-16"))
    simple_config = ConfigParser._simplify_config(config_content)

