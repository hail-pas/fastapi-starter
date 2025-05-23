import asyncio
import pkgutil
import importlib
from logging.config import fileConfig

from loguru import logger
from alembic import context
from sqlalchemy import MetaData, Connection

from config.main import local_configs
from ext.ext_sqlmodel.models.second import SecondBase
from ext.ext_sqlmodel.models.user_center import UserCenterBase

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# config.set_section_option("user_center", "sqlalchemy.url", str(local_configs.extensions.rdb_user_center.url))
# # config.set_section_option("second", "sqlalchemy.url", str(local_configs.extensions.rdb_second.url))


def import_models(package_name):
    package = importlib.import_module(package_name)
    for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        importlib.import_module(module_name)


# Load all models dynamically
import_models("ext.ext_sqlmodel.models")

# db_names = config.set_main_option("databases", "user_center,second")

databases = [
    (
        "user_center",
        local_configs.extensions.rdb_user_center.url,
        local_configs.extensions.rdb_user_center.engine,
        UserCenterBase.metadata,
    ),
    (
        "second",
        local_configs.extensions.rdb_second.url,
        local_configs.extensions.rdb_second.engine,
        SecondBase.metadata,
    ),
]

# target_metadata = [UserCenterBase.metadata, SecondBase.metadata]


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    for name, url, _, metadata in databases:
        print("url is %s" % url)
        logger.info("url is %s" % url)
        logger.info("Migrating database %s" % name)
        file_ = "%s.sql" % name
        logger.info("Writing output to %s" % file_)
        with open(file_, "w") as buffer:
            context.configure(
                url=str(url),
                target_metadata=metadata,
                literal_binds=True,
                dialect_opts={"paramstyle": "named"},
            )

            with context.begin_transaction():
                context.run_migrations(engine_name=name)


def do_run_migrations(connection: Connection, name: str, metadata: MetaData) -> None:
    logger.info("Migrating database %s" % name)
    logger.info("metadata is %s" % metadata)
    logger.info("tables: %s" % metadata.sorted_tables)
    context.configure(
        connection=connection,
        target_metadata=metadata,
        #! upgrade/downgrade token, 不修改这个会导致 upgrade/downgrade template获取不到内容
        upgrade_token=f"{name}_upgrades",
        downgrade_token=f"{name}_downgrades",
        transactional_ddl=True,
        transaction_per_migration=True,
    )
    logger.info("head revision %s" % context.get_head_revision())
    ret = connection.execute(
        "select version_num from alembic_version"
    )

    with connection.begin():
        context.run_migrations(engine_name=name)
    logger.info("Migrated database %s success" % name)


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # current_head_revision = context.get_head_revision()
    # logger.info("current head revision %s" % current_head_revision)
    for name, _, engine, metadata in databases:
        async with engine.connect() as connection:
            # the_raw_aiodbc_connection = (await connection.get_raw_connection()).driver_connection
            # async with the_raw_aiodbc_connection.cursor() as cursor:
            #     await cursor.execute("SELECT @@version")
            #     row = await cursor.fetchone()
            #     logger.info("SQL Server version: %s" % row[0])
            await connection.run_sync(do_run_migrations, name, metadata)

        # await engine.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        asyncio.create_task(run_async_migrations())
    else:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
