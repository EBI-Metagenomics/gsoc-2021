"""Command-line interface."""

import click

from conductor.cli.create import create
from conductor.cli.db import db
from conductor.cli.get import get
from conductor.cli.publish import pub
from conductor.cli.schedule import sched

from .. import __version__


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Conductor console."""
    pass


main.add_command(create)
main.add_command(get)
main.add_command(db)
main.add_command(pub)
main.add_command(sched)
