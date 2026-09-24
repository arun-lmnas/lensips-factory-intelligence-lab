# Gate 0 Bootstrap Report

Scope: reproducible Linux devcontainer for evaluating PM4Py, OCEL, DuckDB,
Pandas/Polars, Graphviz, Jupyter and OFacT/OpenFactoryTwin, without
installing any of these on the host Mac. No application code, process
mining, digital twin, or transformer modeling was implemented — see
[README.md](../README.md) section 13 for the Gate 0 task contract.

## Host / build environment (verified)

- Host OS: macOS, Darwin 25.3.0, arm64 (Apple Silicon)
- Docker Desktop server version: 29.5.3
- Base image: `python:3.12-slim-bookworm` (pulled from Docker Hub)
- Build command: `docker build -t lensips-gate0:test -f .devcontainer/Dockerfile .`
- Devcontainer definition: [.devcontainer/Dockerfile](../.devcontainer/Dockerfile), [.devcontainer/devcontainer.json](../.devcontainer/devcontainer.json)

## Installed foundation versions (verified inside the built image)

| Foundation | Version | Installation method |
|---|---|---|
| Python | 3.12.14 | base image (`python:3.12-slim-bookworm`) |
| uv | 0.5.11 | `pip install uv==0.5.11` (see limitation below) |
| PM4Py | 2.7.14 | `uv pip install pm4py==2.7.14` from PyPI |
| DuckDB | 1.1.3 | `uv pip install duckdb==1.1.3` from PyPI |
| Pandas | 2.2.3 | `uv pip install pandas==2.2.3` from PyPI |
| Polars | 1.17.1 | `uv pip install polars==1.17.1` from PyPI |
| JupyterLab | 4.3.3 | `uv pip install jupyterlab==4.3.3` from PyPI |
| Graphviz (Python binding) | 0.20.3 | `uv pip install graphviz==0.20.3` from PyPI |
| Graphviz (system binary) | 2.43.0 | `apt-get install graphviz libgraphviz-dev` (Debian bookworm) |
| OFacT / OpenFactoryTwin | tag `0.1.0`, commit `b31e24e` | cloned from `https://github.com/OpenFactoryTwin/ofact.git`; see limitation below |
| git | 1:2.39.5 (Debian bookworm) | `apt-get install git` |

Versions of PM4Py, DuckDB, Pandas, Polars, JupyterLab and the Graphviz
Python binding were pinned in the Dockerfile in advance and confirmed to
match exactly after install (`import x; print(x.__version__)` inside the
built image).

## Known limitations / deviations from the original plan

### 1. `uv` installed via PyPI, not the `ghcr.io/astral-sh/uv` image

The Dockerfile originally followed uv's documented `COPY --from=ghcr.io/astral-sh/uv:<version> /uv /uvx ...`
pattern. In this environment, `docker pull ghcr.io/astral-sh/uv:<any tag>`
consistently failed with `denied: denied` (verified with tags `0.5.11`,
`0.12.18`, and `latest`), while `docker pull` from Docker Hub worked
normally. This points to a registry/network restriction on `ghcr.io` in
this Docker Desktop setup, not a problem with the uv image itself.

Worked around by installing uv from PyPI instead (`pip install uv==0.5.11`,
confirmed to exist via the PyPI JSON API before use). Functionally
equivalent for this evaluation; the `uv --version` smoke test passes.

### 2. OFacT `0.1.0` tag has a broken Python packaging manifest

The original Dockerfile assumed OFacT could be `pip install -e`'d from its
`pyproject.toml`. Verified against the actual `0.1.0` tag:

- `pyproject.toml` declares the Poetry package name `dt`.
- No `dt/` folder exists in the repository (the source lives under `ofact/`).
- `uv pip install -e /opt/ofact` fails with
  `poetry.core.masonry.utils.module.ModuleOrPackageNotFoundError: No file/folder found for package dt`.
- The `0.1.0` tag also has no `requirements.txt` (that was assumed
  incorrectly at first and corrected after checking the tag's actual file
  listing).

This is an upstream packaging bug in the `0.1.0` release tag, not something
this repository patches — per repo policy, OFacT source is not forked or
modified.

Workaround used: install OFacT's declared runtime dependencies directly
(`numpy>=1.26.4`, `dill>=0.3.8`, `openpyxl>=3.1.2`; `pandas` is already
installed) and expose the cloned source tree via `PYTHONPATH=/opt/ofact` so
`import ofact` resolves without relying on OFacT's own (broken) packaging.

Consequence: only `import ofact` was verified to work, as a namespace
package (`ofact.__file__` is `None` — there is no top-level `__init__.py`,
so it is a Python namespace package, not a regular one). No OFacT
functionality (state model, simulation, analytics) has been exercised.
Whether the tutorial/example code under `ofact/` and `projects/` in this
tag actually runs was **not** tested — that is explicitly out of scope for
Gate 0 and is deferred to a later gate.

### 3. Not evaluated

- Whether a newer OFacT commit (post-`0.1.0`, on `main`) fixes the
  packaging bug — not checked, since Gate 0 only requires a pinned,
  reproducible version.
- Any actual OFacT simulation/analytics functionality.
- PM4Py functionality beyond `import pm4py` and constructing an empty
  `OCEL` object — deeper OCEL discovery/conformance features are Gate 2+
  concerns.

## Smoke test

Script: [scripts/smoke-test.sh](../scripts/smoke-test.sh)

Reproduce with:

```bash
docker build -t lensips-gate0:test -f .devcontainer/Dockerfile .
docker run --rm -v "$PWD":/workspace -w /workspace lensips-gate0:test bash scripts/smoke-test.sh
```

Actual output (verified run):

```
=== Gate 0 smoke test ===
PASS: Python 3.12
PASS: uv available
PASS: PM4Py import
PASS: PM4Py OCEL support
PASS: DuckDB
PASS: Pandas
PASS: Polars
PASS: Graphviz (Python binding + system binary)
PASS: OFacT import
PASS: Jupyter available
=== Results: 10 passed, 0 failed ===
```

Exit code: `0`.

## Exit criteria check

- [x] Devcontainer builds successfully (`docker build`, exit code 0)
- [x] Container starts successfully (`docker run`, smoke test executed)
- [x] All required smoke tests pass (10/10), with the two upstream issues
      above documented rather than hidden
- [x] Required repository structure present (`.devcontainer/`,
      `experiments/`, `datasets/`, `reports/`, `scripts/`, `README.md`,
      `AGENTS.md`)
- [x] `BOOTSTRAP_REPORT.md` exists (this file)
- [x] No host-level (macOS) development dependencies were installed —
      only Docker was used to build/run the container
- [x] No production repositories were modified
- [x] No LENSIPS application code was created

Gate 0 is complete.
