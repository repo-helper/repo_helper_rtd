#!/usr/bin/env python3
#
#  __init__.py
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
from typing import Dict, Optional, Union

# 3rd party
from apeye import RequestsURL
from click.globals import resolve_color_default
from domdf_python_tools.secrets import Secret
from domdf_python_tools.typing import PathLike
from repo_helper.core import RepoHelper
from requests import Response

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.1.0"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["ReadTheDocsManager"]

# Makes the docs link correctly
Response.__module__ = "requests"


class RequestsURLTS(RequestsURL):
	"""
	Extension of :class:`~apeye.requests_url.RequestsURL` which adds a trailing slash to the end of the URL.

	:param url: The url to construct the :class:`~apeye.url.URL` object from.
	"""

	def __str__(self) -> str:
		"""
		Returns the :class:`~.RequestsURLTS` as a string.
		"""

		return super().__str__() + '/'


RTD_API = RequestsURLTS("https://readthedocs.org/api/v3")


class ReadTheDocsManager(RepoHelper):
	"""
	Subclass of :class:`repo_helper.core.RepoHelper`
	with additional functions to update ReadTheDocs projects.

	:param token: The token to authenticate with the ReadTheDocs API.
	:param target_repo: The path to the root of the repository to manage files for.
	:param managed_message: Message placed at the top of files to indicate that they are managed by ``repo_helper``.
	:param colour: Whether to use coloured output.

	.. versionchanged:: 0.2.3

		Added the ``verbose`` and ``colour`` options.
	"""  # noqa: D400

	colour: Optional[bool]
	"""
	Whether to use coloured output.

	.. versionadded: 0.2.3
	"""

	def __init__(
			self,
			token: str,
			target_repo: PathLike,
			managed_message="This file is managed by 'repo_helper'. Don't edit it directly.",
			*,
			colour: Optional[bool] = True,
			):
		super().__init__(target_repo, managed_message)

		self.token = Secret(token)
		self.colour = resolve_color_default(colour)

	def get_update_json(self) -> Dict[str, Union[Dict[str, str], str]]:
		"""
		Returns the body JSON used to update the project.
		"""

		repo_url = "https://github.com/{username}/{repo_name}".format_map(self.templates.globals)

		return {
				"repository": {"url": repo_url, "type": "git"},
				"language": "en",
				"programming_language": "py",
				"homepage": repo_url,
				}

	def new(self) -> Response:
		"""
		Import this project into ReadTheDocs.
		"""

		body = self.get_update_json()
		body["name"] = self.templates.globals["repo_name"].lower()

		return (RTD_API / "projects").post(
				json=body,
				headers={"Authorization": f"Token {self.token.value}"},
				)

	def update(self) -> Response:
		"""
		Update this project on ReadTheDocs.
		"""

		rtfd_name = self.templates.globals["repo_name"].lower().replace('_', '-')

		return (RTD_API / "projects" / rtfd_name).patch(
				json=self.get_update_json(),
				headers={"Authorization": f"Token {self.token.value}"},
				)
