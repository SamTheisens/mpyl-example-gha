import argparse
import logging
import os
import sys
from logging import Logger
from pathlib import Path
from typing import Optional

from mpyl.build import (
    MpylCliParameters,
    run_mpyl,
)
from mpyl.reporting.targets import ReportAccumulator, Reporter
from mpyl.reporting.targets.github import CommitCheck, PullRequestReporter
from mpyl.reporting.targets.jira import compose_build_status
from mpyl.steps import Step, Meta, ArtifactType, Input, Output
from mpyl.steps.run import RunResult
from mpyl.steps.run_properties import construct_run_properties
from mpyl.utilities.pyaml_env import parse_config
from mpyl.utilities.subprocess import custom_check_output
from rich.console import Console
from rich.logging import RichHandler

def run_gradle(logger: Logger, target: str, task: str) -> Output:
    return custom_check_output(
        logger=logger, command=f"./gradlew {target}:{task} --no-daemon -PmavenUser=$MAVEN_USER -PmavenPassword=$MAVEN_PASSWORD --info",
        use_print=True
    )

class BuildGradle(Step):
    def __init__(self, logger: Logger) -> None:
        super().__init__(
            logger,
            Meta(
                name="Gradle Build",
                description="Build a gradle target",
                version="0.0.1",
                stage='build',
            ),
            produced_artifact=ArtifactType.NONE,
            required_artifact=ArtifactType.NONE,
        )

    def execute(self, step_input: Input) -> Output:
        name = step_input.project_execution.name
        self._logger.info(f"Building project {name}")
        project_name = str(step_input.project_execution.project.root_path).replace("/", ':')
        self._logger.warning(f"Building path {project_name}")

        run_outcome = run_gradle(self._logger, project_name, "bootJar")

        return Output(success=run_outcome.success, message=f"Built {name}", produced_artifact=None)


def main(log: Logger, args: argparse.Namespace):
    config = parse_config(Path(os.environ.get("MPYL_CONFIG_PATH", "mpyl_config.yml")))
    properties = parse_config(Path("run_properties.yml"))
    run_properties = construct_run_properties(config = config, properties=properties)

    cli_parameters = MpylCliParameters(
        local=False,
        tag=args.tag,
        pull_main=True,
        verbose=args.verbose,
        all=args.all,
    )
    check: Optional[Reporter] = None
    github_comment: Optional[Reporter] = None

    if not args.local:
        check = CommitCheck(config=config, logger=log)
        accumulator = ReportAccumulator()

        github_comment = PullRequestReporter(
            config=config,
            compose_function=compose_build_status,
        )
        accumulator.add(
            check.send_report(RunResult(run_properties=run_properties, run_plan={}))
        )

    run_result = run_mpyl(
        run_properties=run_properties,
        cli_parameters=cli_parameters,
        reporter=None,
    )

    if not args.local:
        accumulator.add(check.send_report(run_result))
        accumulator.add(github_comment.send_report(run_result))
        if accumulator.failures:
            log.warning(
                f'Failed to send the following report(s): {", ".join(accumulator.failures)}'
            )
            sys.exit(1)

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
    logging.raiseExceptions = False
    console = Console(
        markup=False,
        width=200,
        no_color=False,
        log_path=False,
        color_system="256",
    )
    logging.basicConfig(
        level="INFO",
        format=FORMAT,
        datefmt="[%X]",
        handlers=[
            RichHandler(markup=False, console=console, show_path=False)
        ],
    )

    parsed_args = parser.parse_args()
    mpl_logger = logging.getLogger("mpyl")
    mpl_logger.info("Starting run.....")
    try:
        main(mpl_logger, parsed_args)
    except Exception as e:
        mpl_logger.warning(f"Unexpected exception: {e}", exc_info=True)
        sys.exit(1)
