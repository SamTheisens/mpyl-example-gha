import argparse
import logging
import os
import sys
from logging import Logger
from pathlib import Path
from mpyl.steps.models import RunProperties
from mpyl.utilities.pyaml_env import parse_config
from mpyl.cli.commands.build.mpyl import (
    run_mpyl,
    MpylRunParameters,
    MpylRunConfig,
    MpylCliParameters,
)


def main(log: Logger, args: argparse.Namespace):
    config = parse_config(Path(os.environ.get("MPYL_CONFIG_PATH", "mpyl_config.yml")))
    properties = parse_config(Path("run_properties.yml"))
    run_properties = RunProperties.from_configuration(
        run_properties=properties, config=config
    )
    params = MpylRunParameters(
        run_config=MpylRunConfig(config=config, run_properties=run_properties),
        parameters=MpylCliParameters(
            local=False,
            tag=args.tag,
            pull_main=False,
            verbose=args.verbose,
            all=args.all,
            target=run_properties.target.value,
        ),
    )

    log.info("Starting build...")
    run_result = run_mpyl(params, None)

    sys.exit(0 if run_result.is_success else 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple MPL pipeline")
    parser.add_argument(
        "--local",
        "-l",
        help="a local developer run",
        default=False,
        action="store_true",
    )
    parser.add_argument("--tag", "-t", help="The name of the tag to build", type=str)
    parser.add_argument(
        "--all",
        "-a",
        help="build and test everything, regardless of the changes that were made",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--dryrun",
        "-d",
        help="don't push or deploy images",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        help="switch to DEBUG level logging",
        default=False,
        action="store_true",
    )
    FORMAT = "%(name)s  %(message)s"

    parsed_args = parser.parse_args()
    mpl_logger = logging.getLogger("mpyl")
    mpl_logger.info("Starting run.....")
    try:
        main(mpl_logger, parsed_args)
    except Exception as e:
        mpl_logger.warning(f"Unexpected exception: {e}", exc_info=True)
        sys.exit(1)
