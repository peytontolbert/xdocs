xdocs/
  docs/
    quickstart.md
    api.md
  src/your_pkg/
  tests/
  tools/
    xdocs/
      __init__.py
      cli.py              # xdocs run / xdocs extract / xdocs accept
      extract.py          # parse markdown -> snippet IR
      run.py              # execute snippets in sandbox
      assert.py           # snapshot + structured asserts
      normalize.py        # stable outputs (strip timestamps, paths)
      manifest.py         # docs manifest + cache key
  xdocs.yaml              # optional per-repo config
  pyproject.toml
  .github/workflows/docs.yml
