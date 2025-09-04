import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alembic.config import Config
from alembic import command

# Set up the Alembic configuration
alembic_cfg = Config("alembic.ini")

# Override the database URL from environment if available
db_url = os.environ.get("DATABASE_URL")
if db_url is not None:
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

# Run the upgrade to the latest revision
command.upgrade(alembic_cfg, "head")
print("Migration completed successfully!")
