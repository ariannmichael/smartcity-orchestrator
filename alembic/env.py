import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

from app.core.config import settings
from app.core.db import Base

from app.infra.persistence.models.event import Event
from app.infra.persistence.models.outbox import OutboxMessage
target_metadata = Base.metadata


def get_database_url() -> str:
    """Get database URL, replacing 'db' hostname with 'localhost' for local development."""
    url = os.getenv("ALEMBIC_DATABASE_URL") or settings.DATABASE_URL
    
    # Only replace 'db' with 'localhost' when running locally (outside Docker)
    # Inside Docker containers, we should use the service name 'db'
    # Check if we're running inside Docker by looking for /.dockerenv
    is_inside_docker = os.path.exists("/.dockerenv")
    
    if not is_inside_docker and "@db" in url:
        # Replace 'db' hostname with 'localhost' when running locally
        # Common format: postgresql://user:pass@db:5432/dbname -> postgresql://user:pass@localhost:5432/dbname
        url = url.replace("@db", "@localhost")
    
    return url

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url") or get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
