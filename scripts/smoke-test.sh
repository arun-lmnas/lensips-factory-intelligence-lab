#!/usr/bin/env bash
# Gate 0 smoke test: verify the evaluation foundations are importable/usable
# inside the devcontainer. Exits non-zero if any REQUIRED foundation fails.
set -u

pass=0
fail=0

check() {
  local name="$1"
  shift
  if "$@" >/tmp/smoke-test-last.log 2>&1; then
    echo "PASS: ${name}"
    pass=$((pass + 1))
  else
    echo "FAIL: ${name}"
    sed 's/^/    /' /tmp/smoke-test-last.log
    fail=$((fail + 1))
  fi
}

echo "=== Gate 0 smoke test ==="

check "Python 3.12" python3 -c "import sys; assert sys.version_info[:2] == (3, 12), sys.version"

check "uv available" uv --version

check "PM4Py import" python3 -c "import pm4py; print(pm4py.__version__)"

check "PM4Py OCEL support" python3 -c "
import pm4py
from pm4py.objects.ocel.obj import OCEL
ocel = OCEL()
assert ocel is not None
"

check "DuckDB" python3 -c "
import duckdb
con = duckdb.connect()
assert con.execute('select 1').fetchone() == (1,)
"

check "Pandas" python3 -c "import pandas as pd; df = pd.DataFrame({'a': [1, 2]}); assert len(df) == 2"

check "Polars" python3 -c "import polars as pl; df = pl.DataFrame({'a': [1, 2]}); assert df.height == 2"

check "Graphviz (Python binding + system binary)" python3 -c "
import graphviz
g = graphviz.Digraph()
g.node('a')
g.node('b')
g.edge('a', 'b')
g.pipe(format='svg')
"

check "OFacT import" python3 -c "import ofact"

check "Jupyter available" python3 -c "import jupyterlab"

echo "=== Results: ${pass} passed, ${fail} failed ==="

if [ "${fail}" -gt 0 ]; then
  exit 1
fi
exit 0
