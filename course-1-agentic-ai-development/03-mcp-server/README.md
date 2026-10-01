# Module 3: MCP server basics

MCP (Model Context Protocol) standardizes how a tool-providing server exposes
capabilities to any MCP-compatible client (Claude Code, Claude Desktop, etc.)
instead of every app writing bespoke tool-calling glue. A server declares
tools with the same name / description / schema shape as native tool use,
and the client handles discovery and invocation over stdio or HTTP
transport. FastMCP, the reference Python SDK, turns a decorated function into
a spec-compliant MCP tool in a few lines.

## Run the working example

```bash
python mcp_server.py
```

It blocks, listening on stdio — that's expected (Ctrl+C to stop). Plain
`python` is only a sanity check ("does it import and start without
crashing"); there's no client attached, so there's nothing to interact
with. To actually exercise it interactively, use the MCP Inspector,
which launches the server *and* a web UI for calling its tools by hand:

```bash
mcp dev mcp_server.py
```

## Exercise

The exercise lives in a separate file, `exercise_starter.py`, and the
`mcp dev` command only inspects whatever file you point it at — so the
order matters:

1. Stop any running `mcp dev mcp_server.py` session (Ctrl+C) — it's
   inspecting the *working example*, not the exercise file.
2. Open `exercise_starter.py` and add a second tool, `list_files(pattern:
   str = "*.py")`, using `CODEBASE_ROOT.rglob(pattern)`.
3. Run `mcp dev exercise_starter.py` and confirm both tools'
   docstrings show up correctly as their MCP descriptions.

## What success looks like

You can explain why `is_relative_to` matters in `read_file` — it's a
path-traversal guard, the same class of control covered in Course 2's
least-privilege module (`course-2-ai-security-governance/`). It stops
`relative_path="../../etc/passwd"`, but note it's necessary, not
sufficient: because the check runs on the *resolved* path (`.resolve()`
follows symlinks before comparing), a symlink inside `CODEBASE_ROOT`
pointing outside it is still caught here — the gap that remains is
TOCTOU (the file on disk changing between the check and the read), which
matters for a multi-tenant server but not for this single-user exercise.

## Security in real-world deployments

The model calling these tools is an untrusted caller, even though it
looks cooperative. A weird prompt, a prompt injection hiding in a
document the model read, or a bug in `is_relative_to` could otherwise
turn "read one project file" into an arbitrary-file-read primitive.
Real deployments layer several independent controls so no single one —
including the Python-level path check — is the only thing standing
between "read one file" and "read anything on the host."

### Root vs. sudo vs. least privilege

- **root** is a literal user account (UID 0) with no permission checks
  applied to it — it can read/write/execute anything, change ownership
  of anything, bind any port, load kernel modules.
- **sudo** isn't a privilege itself — it's a mechanism for a normal user
  to temporarily run a command as another user (usually root), governed
  by `/etc/sudoers`. It exists so elevation is deliberate, scoped, and
  logged, not so services run as root by default.
- **An MCP server should never run as root, and should never need
  sudo.** It has one job — expose a narrow set of file operations. If it
  runs as root, the `is_relative_to` check becomes your *only* line of
  defense; a bug there (or a cleverly crafted path) becomes a full
  filesystem compromise instead of a contained mistake. Run it as a
  dedicated unprivileged service account instead, so the OS itself
  refuses what the app-level check might miss.

### File permissions as a second, independent wall

App logic (`is_relative_to`) says "this tool shouldn't return files
outside the project." OS permissions should say the same thing
independently, so a bug in one doesn't undermine the other:

```bash
chown -R mcp-svc:mcp-svc /path/to/sample_project   # dedicated user owns only this tree
chmod -R u=rX,go= /path/to/sample_project          # read-only, no group/other access
```

If a tool never needs to write, don't grant the service account write
(`w`) permission on that tree at all — then even a code bug that tries
to write gets refused by the OS, not just by application logic.

### Process isolation: containers, and why scope changes the design

`read_file` and `list_files` only need read access, so a read-only
bind-mount is enough. But plenty of real tools need more — the
classic case is a **refactor tool**: something that greps across the
codebase for a symbol (`grep -rn old_name .`) and then rewrites every
occurrence (`old_name` → `new_name`) across multiple files. That tool
needs:

- **Read** access to the whole codebase (to find every occurrence, not
  just files it was told about).
- **Write** access to modify files in place.
- Possibly a **shell** or subprocess to run `grep`/`sed`/an AST-rewrite
  tool.

That's a much bigger blast radius than `read_file`, so the containment
strategy has to be more deliberate, not looser:

1. **One container per task, not a long-lived shared one.** Spin up a
   fresh container scoped to a single refactor session, bind-mount
   *only* the target repo into it (e.g. `-v $(pwd):/workspace`), and
   destroy the container when the task ends. The tool's "world" is
   `/workspace` and nothing else — there is no `/etc/passwd`, no other
   project's code, no host credentials for it to reach, because they
   were never mounted in.
2. **Non-root user inside the container**, same as the bare-metal case
   — `USER mcp-svc` in the Dockerfile, not `root`. Root *inside* a
   container is still root with respect to that container's filesystem
   and, without extra hardening, a container escape turns into host
   root.
3. **Read-write only where needed, read-only everywhere else.** Mount
   the target repo read-write, but if the tool needs reference data
   (style guides, lint config from elsewhere) mount those read-only
   (`-v $(pwd)/configs:/configs:ro`).
4. **No network egress**, unless the tool genuinely needs to call out
   (e.g., to fetch a package). A refactor tool that can read your whole
   repo *and* phone home is the exfiltration scenario the isolation is
   meant to prevent.
5. **Resource limits** (`--memory`, `--cpus`, or cgroup limits) so a
   runaway rewrite (e.g., a bad regex matching everything) can't
   exhaust the host.
6. **Diff before commit, always.** Have the tool return a diff/patch
   for the calling agent (or a human) to review rather than silently
   committing changes — the container boundary stops the tool from
   touching the *host*, but it doesn't stop the tool from making a bad
   *edit*. Those are different failure modes and need different
   controls: containment for "can it reach things it shouldn't,"
   review for "did it do the right thing to what it could reach."
7. **Audit log of every command run inside the container** (the exact
   `grep`/rewrite invocation, files touched, byte counts changed) —
   useful for debugging and for reconstructing what happened if a
   refactor goes wrong.

The general pattern: **scope the container to the task, not to the
tool.** `read_file` can live in a long-running, read-only-mounted
server because its access pattern never changes. A refactor tool's
access pattern is inherently wider (read+write, whole repo, maybe
shell) and time-bounded (one refactor, then done) — so it fits an
ephemeral, per-invocation container much better than a persistent
service, and the destroy-after-use step is itself a security control:
whatever the tool touched, the container (and any transient state)
disappears when the task ends.

### Transport matters: stdio vs. HTTP

This module's server runs on `transport="stdio"` — the client
(Claude Code/Desktop) spawns it directly as a subprocess. There's no
network exposure; the trust boundary is "whoever can run this process
on this machine," so the example doesn't need auth.

The moment a server moves to HTTP transport (remote or multi-user
clients), the threat model changes:

- **Authentication** (API keys, OAuth, mTLS) — otherwise anyone who can
  reach the port can invoke `read_file`/the refactor tool with
  arbitrary inputs.
- **Per-caller authorization scoping** — user A's session shouldn't
  reach user B's project even under a shared deployment.
- **TLS in transit**, since tool inputs/outputs may carry source code,
  secrets, or credentials.
- **Rate limiting and audit logging**, since the server is now a remote
  data-access/code-modification API, not a local dev convenience.

### Checklist: toy version vs. production version

| Control | This exercise | Production |
|---|---|---|
| Run-as user | your login user | dedicated unprivileged service account, never root |
| Path check | `is_relative_to` | same, plus reject symlinks/`..` early as defense-in-depth |
| Filesystem scope | whole disk technically reachable, app-checked | container/bind-mount so nothing else exists |
| Write access | none needed, none given | explicit allow-list of writable subpaths, ephemeral container per write-capable task |
| Transport | stdio, implicit trust | HTTP + auth + TLS + per-caller scoping |
| Observability | none | audit log of every tool call and, for write tools, a reviewable diff |
| Resource limits | none | cgroup/ulimit caps on CPU, memory, file count |
