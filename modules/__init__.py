"""Legacy compatibility namespace.

Historically this repository used ``modules.*`` package paths. Runtime code has
been reorganized under ``app`` and ML code under ``ml.lib``; this package is
kept to avoid breaking external imports and serialized model artifacts that
still reference the legacy path.
"""

__all__ = ["ml_coder"]
