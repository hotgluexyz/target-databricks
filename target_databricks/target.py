"""databricks target class."""

from __future__ import annotations

import json

from pathlib import PurePath
from singer_sdk import typing as th
from singer_sdk.target_base import Target

from target_databricks.sinks import databricksSink
from target_databricks.auth import Auth


class Targetdatabricks(Target):
    """Sample target for databricks."""

    name = "target-databricks"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "host",
            th.StringType,
            secret=True,  # Flag config as protected.
            description="Databricks host for connection",
        ),
        th.Property(
            "client_id",
            th.StringType,
            secret=True,  # Flag config as protected.
            description="OAuth 2 Client ID",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            secret=True,  # Flag config as protected.
            description="OAuth 2 Client Secret",
        ),
        th.Property(
            "refresh_token",
            th.StringType,
            secret=True,  # Flag config as protected.
            description="OAuth 2 Refresh Token",
        ),
        th.Property(
            "access_token",
            th.StringType,
            secret=True,  # Flag config as protected.
            description="Databricks Personal Access Token",
        ),
        th.Property(
            "http_path",
            th.StringType,
            secret=True,  # Flag config as protected.
            description="Databricks http path for connection",
        ),
        th.Property(
            "catalog",
            th.StringType,
            secret=True,  # Flag config as protected.
            description="Databricks catalog for connection",
        ),
        th.Property(
            "aws_access_key_id",
            th.StringType,
            secret=True,  # Flag config as protected.
            description="AWS access key for staging files",
        ),
        th.Property(
            "aws_secret_access_key",
            th.StringType,
            secret=True,  # Flag config as protected.
            description="AWS secret access key for staging files",
        ),
        th.Property(
            "aws_region",
            th.StringType,
            secret=True,  # Flag config as protected.
            description="AWS region for staging files",
        ),
        th.Property(
            "aws_profile_name",
            th.StringType,
            secret=True,  # Flag config as protected.
            description="AWS profile name for staging files",
        ),
        th.Property(
            "bucket",
            th.StringType,
            secret=False,
            description="AWS s3 bucket for staging files",
        ),
        th.Property(
            "prefix",
            th.StringType,
            secret=False,
            description="AWS s3 bucket prefix for staging files",
        ),
        th.Property(
            "default_target_schema",
            th.StringType,
            secret=False,
            description="schema name to push the records to, (table name will be stream name by default)",
        ),
        th.Property(
            "clean_up_staged_files",
            th.BooleanType,
            secret=False,
            description="to clean staged files after processing the data",
        ),
        th.Property(
            "include_process_date",
            th.BooleanType,
            secret=False,
            description="to include of a timestamp when the record was processed",
        ),
    ).to_dict()

    default_sink_class = databricksSink

    def __init__(
        self,
        config=None,
        parse_env_config: bool = False,
        validate_config: bool = True
    ) -> None:
        self.config_file_path = None
        if isinstance(config, str) or isinstance(config, PurePath):
            self.config_file_path = str(config)
        elif isinstance(config, list):
            self.config_file_path = str(config[0])
        elif isinstance(config, dict):
            raise Exception("Config must be a file path or a list of file paths")
        elif config is None:
            raise Exception("Config not provided")

        super().__init__(
            config=config,
            parse_env_config=parse_env_config,
            validate_config=validate_config,
        )

        self.auth = Auth(self)

    def deserialize_json(self, line: str) -> dict:
        """Override base target's method to overcome Decimal cast,
        only applied when generating parquet schema from tap schema.

        :param line: serialized record from stream
        :type line: str
        :return: deserialized record
        :rtype: dict
        """
        try:
            return json.loads(line)  # type: ignore[no-any-return]
        except json.decoder.JSONDecodeError as exc:
            self.logger.error("Unable to parse:\n%s", line, exc_info=exc)
            raise


if __name__ == "__main__":
    Targetdatabricks.cli()
