"""Sparse typed-fact schemas for constrained LLM extraction.

Claude's structured outputs limit a request to 24 optional parameters and 16
union-typed parameters, so a record schema with nullable fields cannot be used
directly. Instead the model returns rows plus typed facts. Every property is
required, there are no unions, and a field the note never mentions is simply
absent. Per-field value checks happen client-side via ``FieldSpec.coerce``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Iterable, Literal

FactKind = Literal["enum", "bool", "number", "integer", "text"]
ASSERTIONS = ("active", "negated", "planned", "historical", "uncertain")
FACT_ARRAYS = {
    "enum": "enum_facts",
    "bool": "bool_facts",
    "number": "number_facts",
    "integer": "number_facts",
    "text": "text_facts",
}


class FactValueError(ValueError):
    pass


@dataclass(frozen=True)
class FieldSpec:
    collection: str
    field: str
    kind: FactKind
    values: tuple[str, ...] = ()
    minimum: float | None = None
    maximum: float | None = None
    max_length: int | None = None

    @property
    def path(self) -> str:
        return f"{self.collection}.{self.field}"

    def coerce(self, value: Any) -> Any:
        if self.kind == "enum":
            if value not in self.values:
                raise FactValueError(f"{self.path}: {value!r} not allowed")
            return value
        if self.kind == "bool":
            if not isinstance(value, bool):
                raise FactValueError(f"{self.path}: expected boolean")
            return value
        if self.kind in {"number", "integer"}:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise FactValueError(f"{self.path}: expected number")
            if self.kind == "integer":
                if float(value) != int(value):
                    raise FactValueError(f"{self.path}: expected integer")
                value = int(value)
            else:
                value = float(value)
            if self.minimum is not None and value < self.minimum:
                raise FactValueError(f"{self.path}: below {self.minimum}")
            if self.maximum is not None and value > self.maximum:
                raise FactValueError(f"{self.path}: above {self.maximum}")
            return value
        if not isinstance(value, str) or not value.strip():
            raise FactValueError(f"{self.path}: expected text")
        value = value.strip()
        if self.max_length is not None and len(value) > self.max_length:
            raise FactValueError(f"{self.path}: longer than {self.max_length}")
        return value


@dataclass(frozen=True)
class CollectionSpec:
    name: str
    fields: tuple[FieldSpec, ...]
    singleton: bool = False
    # Foreign-key field -> parent collection.
    parents: dict[str, str] = field(default_factory=dict)


def _obj(properties: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(properties),
        "properties": properties,
    }


def _array(item: dict[str, Any]) -> dict[str, Any]:
    return {"type": "array", "items": item}


def _string_enum(values: Iterable[str]) -> dict[str, Any]:
    return {"type": "string", "enum": sorted(set(values))}


def build_facts_schema(
    collections: Iterable[CollectionSpec],
    *,
    missing_reasons: Iterable[str],
    unresolved_kinds: Iterable[str],
) -> dict[str, Any]:
    collections = tuple(collections)
    specs = [spec for collection in collections for spec in collection.fields]
    by_kind: dict[str, list[FieldSpec]] = {}
    for spec in specs:
        by_kind.setdefault(FACT_ARRAYS[spec.kind], []).append(spec)
    row_collections = [c.name for c in collections if not c.singleton]
    parent_fields = sorted({key for c in collections for key in c.parents})
    assertion = _string_enum(ASSERTIONS)
    properties: dict[str, Any] = {
        "rows": _array(
            _obj(
                {
                    "collection": _string_enum(row_collections),
                    "local_id": {"type": "string"},
                    "parents": _array(
                        _obj({"field": _string_enum(parent_fields), "local_id": {"type": "string"}})
                    ),
                    "anchor_quote": {"type": "string"},
                }
            )
        )
    }
    value_types = {
        "enum_facts": _string_enum(
            v for spec in by_kind.get("enum_facts", []) for v in spec.values
        ),
        "bool_facts": {"type": "boolean"},
        "number_facts": {"type": "number"},
        "text_facts": {"type": "string"},
    }
    for array_name in ("enum_facts", "bool_facts", "number_facts", "text_facts"):
        members = by_kind.get(array_name, [])
        if not members:
            continue
        properties[array_name] = _array(
            _obj(
                {
                    "local_id": {"type": "string"},
                    "field": _string_enum(spec.path for spec in members),
                    "value": value_types[array_name],
                    "assertion": assertion,
                    "evidence_quote": {"type": "string"},
                }
            )
        )
    properties["missing_facts"] = _array(
        _obj(
            {
                "local_id": {"type": "string"},
                "field": _string_enum(spec.path for spec in specs),
                "reason": _string_enum(missing_reasons),
                "evidence_quote": {"type": "string"},
            }
        )
    )
    properties["unresolved"] = _array(
        _obj(
            {
                "kind": _string_enum(unresolved_kinds),
                "note": {"type": "string"},
                "evidence_quote": {"type": "string"},
            }
        )
    )
    return _obj(properties)


def schema_digest(schema: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest()


def schema_complexity(schema: dict[str, Any]) -> dict[str, int]:
    """Count the structured-output limits: optional properties and union-typed params."""
    optional = unions = 0

    def walk(node: Any) -> None:
        nonlocal optional, unions
        if isinstance(node, dict):
            if "anyOf" in node or isinstance(node.get("type"), list):
                unions += 1
            props = node.get("properties")
            if isinstance(props, dict):
                optional += len(set(props) - set(node.get("required", [])))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(schema)
    return {"optional_properties": optional, "union_parameters": unions}


__all__ = [
    "ASSERTIONS",
    "CollectionSpec",
    "FACT_ARRAYS",
    "FactValueError",
    "FieldSpec",
    "build_facts_schema",
    "schema_complexity",
    "schema_digest",
]
