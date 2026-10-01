"""Module 3 — exercise: add a list_files tool alongside read_file.

Run `mcp dev exercise_starter.py` and confirm both tools appear with
correct descriptions in the Inspector.
"""

from pathlib import Path
# Path traversal / symlink checks below rely on pathlib's resolve() and
# is_relative_to() rather than string manipulation, which is what makes
# them reliable.

from mcp.server.fastmcp import FastMCP
# FastMCP is the reference Python SDK: it turns a decorated function into
# a spec-compliant MCP tool (name, description, JSON-schema input) without
# hand-writing the MCP protocol handshake yourself.

# The server's identity as seen by an MCP client (Claude Code, Claude
# Desktop, the MCP Inspector) when it lists available servers/tools.
mcp = FastMCP("codebase-reader")

# The one directory both tools below are allowed to touch. Resolved once
# at import time to an absolute path so every later comparison is against
# a fixed, canonical root rather than a possibly-relative or symlinked one.
CODEBASE_ROOT = (Path(__file__).parent.parent / "sample_project").resolve()


# The decorator registers this function as an MCP tool. FastMCP reads the
# function name ("read_file"), its type hints (to build the JSON-schema
# input the client validates against), and the docstring (to build the
# tool's description — the text the model uses to decide when to call it).
@mcp.tool()
def read_file(relative_path: str) -> str:
    """Read a file's contents from the codebase directory. Path is relative to the project root."""
    # Join the caller-supplied path onto the trusted root, then resolve
    # it. resolve() collapses "..", "." and follows symlinks, so this is
    # the *actual* file the OS would open — not just the literal string
    # the caller passed.
    target = (CODEBASE_ROOT / relative_path).resolve()

    # The core security control: after resolving, confirm the target is
    # still inside CODEBASE_ROOT. This is what stops
    # relative_path="../../etc/passwd" (or a symlink inside the codebase
    # that points outside it) from escaping the sandbox. Doing the check
    # on the *resolved* path, after joining, is what makes it reliable —
    # checking the raw string first is the common way this guard gets
    # built wrong.
    if not target.is_relative_to(CODEBASE_ROOT):
        raise ValueError("Path escapes the codebase root.")

    # Only reached if the path is safely inside the sandbox — read and
    # return the file's contents as the tool's result (an MCP
    # tool_result under the hood).
    return target.read_text()


@mcp.tool()
def list_files(pattern: str = "*.py") -> str:
    """List files under the codebase directory matching a glob pattern (default: *.py)."""
    # rglob walks CODEBASE_ROOT recursively and only ever yields paths
    # that live under it — unlike read_file, there's no caller-supplied
    # path to join onto the root, so there's no traversal surface here.
    # The pattern itself (e.g. "*.py") only selects filenames/extensions;
    # it can't be used to climb out of the directory the way a path can.
    matches = sorted(CODEBASE_ROOT.rglob(pattern))

    # Return paths relative to CODEBASE_ROOT, not target.resolve() as an
    # absolute path — the caller only needs to know where a file sits
    # inside the project, and relative paths avoid leaking the absolute
    # filesystem layout of the host the server happens to be running on.
    relative_paths = [str(match.relative_to(CODEBASE_ROOT)) for match in matches if match.is_file()]
    return "\n".join(relative_paths)


if __name__ == "__main__":
    # Serve over stdio: the client spawns this script as a subprocess and
    # talks MCP over its stdin/stdout. This blocks forever (Ctrl+C to
    # stop) because it's an event loop waiting for tool-call requests —
    # there is no separate "server" process to connect to over a port.
    mcp.run(transport="stdio")
