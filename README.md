# xdocs (Docs-as-Tests)

`xdocs` is a small **executable documentation** runner: Markdown fenced code blocks marked `xdocs` are executed and verified like tests (snapshots/assertions), locally and in CI.

## Install (from GitHub)

Once you push this repo to GitHub, other projects can install it directly:

```bash
pip install "xdocs @ git+https://github.com/YOUR_ORG/xdocs.git"
```

## Authoring

In Markdown:

```markdown
```python xdocs
print("Hello from docs")
```
````

## Running locally

```bash
pip install -e ".[dev]"  # in the repo you're xdocs-ing
pytest
```

To (re)generate snapshots:

```bash
XDOCS_ACCEPT=1 pytest
```

## Bootstrap another repo

From the root of the target repo:

```bash
pip install "xdocs @ git+https://github.com/YOUR_ORG/xdocs.git"
xdocs init --ci-install "xdocs @ git+https://github.com/YOUR_ORG/xdocs.git"
```


