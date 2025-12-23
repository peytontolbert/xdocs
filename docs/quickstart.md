# Quickstart

This is an **executable** quickstart: any fenced block marked `xdocs` is run in CI.

## Hello

```python xdocs
print("Hello from executable docs")
```

## Inline expectation

```python xdocs expect="stdout:Hello"
print("Hello from executable docs")
```


