# Gate 0 evaluation environment for LENSIPS Factory Intelligence Lab.
# Purpose: give PM4Py, OCEL, DuckDB, Pandas/Polars, Graphviz, Jupyter and
# OFacT/OpenFactoryTwin a reproducible Linux home, without installing any of
# it on the host Mac. Nothing here builds an application.

FROM python:3.12-slim-bookworm

# graphviz: required by PM4Py for process-model visualization.
# git: required to fetch OFacT (it is not published on PyPI; see reports/BOOTSTRAP_REPORT.md).
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    graphviz \
    libgraphviz-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# uv: fast, reproducible Python package/dependency manager.
# Installed via pip from PyPI rather than the ghcr.io/astral-sh/uv image:
# ghcr.io pulls were denied in this environment's network/Docker setup
# (docker.io pulls work fine), so PyPI is the more reliable official source
# here. See reports/BOOTSTRAP_REPORT.md.
RUN pip install --no-cache-dir "uv==0.5.11"

ENV UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace

# Pin the evaluation foundations explicitly (see reports/BOOTSTRAP_REPORT.md
# for the rationale behind each version).
RUN uv pip install --system \
    "pm4py==2.7.14" \
    "duckdb==1.1.3" \
    "pandas==2.2.3" \
    "polars==1.17.1" \
    "jupyterlab==4.3.3" \
    "graphviz==0.20.3"

# OFacT / OpenFactoryTwin has no PyPI package; it is a monorepo that must be
# cloned from source. Pin to the 0.1.0 tag (initial public release) for
# reproducibility.
#
# KNOWN UPSTREAM PACKAGING BUG (verified, not worked around by modifying
# OFacT itself, per repo policy): at the 0.1.0 tag, pyproject.toml declares
# the poetry package name "dt" but ships no "dt/" folder (the code lives
# under "ofact/"), so `pip install -e .` / `uv pip install -e .` fails with
# ModuleOrPackageNotFoundError. We install its declared runtime dependencies
# directly instead, and expose the source tree via PYTHONPATH so `import
# ofact` works without needing OFacT's own packaging. See
# reports/BOOTSTRAP_REPORT.md.
RUN git clone --branch 0.1.0 --depth 1 https://github.com/OpenFactoryTwin/ofact.git /opt/ofact \
    && uv pip install --system "numpy>=1.26.4" "dill>=0.3.8" "openpyxl>=3.1.2"

ENV PYTHONPATH=/opt/ofact

CMD ["sleep", "infinity"]
