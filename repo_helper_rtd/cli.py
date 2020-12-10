#!/usr/bin/env python3
#
#  cli.py
"""
Manage ReadTheDocs documentation with ``repo-helper``.
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import sys
from functools import partial
from typing import Optional

# 3rd party
import click
from consolekit import CONTEXT_SETTINGS
from consolekit.options import colour_option, version_option
from repo_helper.cli import cli_group

# this package
from repo_helper_rtd.options import token_option, version_callback

__all__ = [
		"rtd",
		"new",
		"update",
		"rtd_command",
		]


@version_option(version_callback)
@cli_group(invoke_without_command=False)
def rtd():
	"""
	Manage a ReadTheDocs project.
	"""


rtd_command = partial(rtd.command, context_settings=CONTEXT_SETTINGS)


@colour_option()
@token_option()
@rtd_command()
def new(token: str, colour: Optional[bool] = None):
	"""
	Create a new ReadTheDocs project.
	"""

	# 3rd party
	from domdf_python_tools.paths import PathPlus

	# this package
	from repo_helper_rtd import ReadTheDocsManager

	manager = ReadTheDocsManager(token, PathPlus.cwd(), colour=colour)
	response = manager.new()

	print(response)
	if response.status_code // 100 == 2:
		project_name = manager.templates.globals["repo_name"].lower().replace('_', '-')
		click.echo(f"Success! View the project page at https://readthedocs.org/projects/{project_name}")
		sys.exit(0)

	sys.exit(1)


@colour_option()
@token_option()
@rtd_command()
def update(token: str, colour: Optional[bool] = None):
	"""
	Update the ReadTheDocs project.
	"""

	# 3rd party
	from domdf_python_tools.paths import PathPlus

	# this package
	from repo_helper_rtd import ReadTheDocsManager

	response = ReadTheDocsManager(token, PathPlus.cwd(), colour=colour).update()

	print(response)
	if response.status_code // 100 == 2:
		click.echo("Up to date!")
		sys.exit(0)

	sys.exit(1)
