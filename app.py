from config.conf import Config
from src.mad_migration import MadMigration

config = Config("test.yaml")

if __name__ == "__main__":
    a = MadMigration(config)
    a.test_func()
