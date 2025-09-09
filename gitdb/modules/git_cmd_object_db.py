"""Git object database using the git command-line interface.

This module is part of GitPython and released under the BSD 3-Clause License.
"""

__all__ = ["GitCmdObjectDB", "GitDB"]

from typing import TYPE_CHECKING
from git.types import PathLike
from gitdb.base import OInfo, OStream
from gitdb.db import GitDB, LooseObjectDB
from gitdb.exc import BadObject
from git.util import bin_to_hex, hex_to_bin
from git.exc import GitCommandError

if TYPE_CHECKING:
    from git.cmd import Git


class GitCmdObjectDB(LooseObjectDB):
    """Git object database using the `git` command for access.

    This database supports loose objects, pack files, and alternates.
    Object creation is limited to the loose object store.
    """

    def __init__(self, root_path: PathLike, git: "Git") -> None:
        super().__init__(root_path)
        self._git = git

    def info(self, binsha: bytes) -> OInfo:
        """Retrieve object header using `git cat-file`.

        Args:
            binsha: Binary SHA of the object.

        Returns:
            OInfo: Object metadata.
        """
        hexsha, typename, size = self._git.get_object_header(bin_to_hex(binsha))
        return OInfo(hex_to_bin(hexsha), typename, size)

    def stream(self, binsha: bytes) -> OStream:
        """Stream object data using `git cat-file`.

        Args:
            binsha: Binary SHA of the object.

        Returns:
            OStream: Streamed object content.
        """
        hexsha, typename, size, stream = self._git.stream_object_data(bin_to_hex(binsha))
        return OStream(hex_to_bin(hexsha), typename, size, stream)

    def partial_to_complete_sha_hex(self, partial_hexsha: str) -> bytes:
        """Resolve a partial SHA to a full binary SHA.

        Args:
            partial_hexsha: Partial hexadecimal SHA.

        Returns:
            bytes: Full binary SHA.

        Raises:
            BadObject: If the object is not found or ambiguous.
        """
        try:
            hexsha, *_ = self._git.get_object_header(partial_hexsha)
            return hex_to_bin(hexsha)
        except (GitCommandError, ValueError) as e:
            raise BadObject(partial_hexsha) from e
