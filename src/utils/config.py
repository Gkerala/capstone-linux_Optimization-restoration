import json
import jsonschema
import os


class ConfigLoader:
    def __init__(self, config_path, schema_path=None):
        self.config_path = config_path
        self.schema_path = schema_path
        self.config = None
        self.schema = None

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def get_config(self):
        if self.config is None:
            raise ValueError("Config not loaded. Call 'load_config()' first.")
        return self.config

    def load_schema(self):
        if not self.schema_path or not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def validate(self):
        if self.schema is None:
            raise ValueError("Schema not loaded. Call 'load_schema()' first.")
        if self.config is None:
            raise ValueError("Config not loaded. Call 'load_config()' first.")
        jsonschema.validate(instance=self.config, schema=self.schema)

    def save_config(self, new_config):
        if self.schema:
            jsonschema.validate(instance=new_config, schema=self.schema)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(new_config, f, indent=4)
        self.config = new_config  # 내부 config도 업데이트

