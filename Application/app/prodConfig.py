from .config import Config

# The contents of this class differ on the production server, this is a placeholder
### Defines the production server configurations
class ProdConfig(Config):
    raise RuntimeError("Incorrectly set FLASK environment variable => should be \'development\'")