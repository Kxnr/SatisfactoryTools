from pydantic import BaseModel

CONFIG_PATH = "config.toml"

class Config(BaseModel):
    class Paths(BaseModel):
        saved_nodes: str
        satisfactory_docs: str

    paths: Paths

