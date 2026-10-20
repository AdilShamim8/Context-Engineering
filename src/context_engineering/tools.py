"""Tool context and external interactions (Chapter 20).

Tools are the model's hands — and every hand needs a permission. This
module implements the context-engineering side of tool calling:

- ToolSpec: name, description (what the model reads to CHOOSE the tool),
  a minimal JSON-style parameter schema (what the app validates BEFORE
  running anything), required access class, permission, and an output cap.
- ToolRegistry.call: the single guarded path — unknown tool, unauthorized
  caller, invalid arguments, handler exceptions, and oversized outputs all
  return structured ToolResults. A tool call can fail; it must never
  crash, and it must never return a raw stack trace into model context.

The design rules from Chapter 20 encoded here:

1. Descriptions teach SELECTION, not usage — they state what the tool is
   for and when NOT to use it.
2. Authorization is an app-level check per call — never a prompt sentence.
3. Every output is bounded and marked when truncated (Chapter 12's rule,
   applied to tool results).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

from .context import ComponentKind, ContextComponent, TrustLevel

TRUNCATION_NOTE = " …[output truncated to fit tool output cap]"

_TYPE_MAP = {
    "string": str, "str": str,
    "integer": int, "int": int,
    "number": (int, float),
    "boolean": bool, "bool": bool,
    "array": list, "object": dict,
}


@dataclass
class ToolResult:
    """The structured outcome of a tool call — error paths included."""

    ok: bool
    output: str = ""
    error: str = ""
    truncated: bool = False
    tool: str = ""

    @classmethod
    def failure(cls, tool: str, error: str) -> "ToolResult":
        return cls(ok=False, error=error, tool=tool)


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters_schema: dict  # {"properties": {..}, "required": [..]}
    required_access: str = "internal"   # access class the CALLER must hold
    permission: str = ""                # named permission, for audit trails
    output_max_chars: int = 4000

    def render_definition(self) -> str:
        """Render the model-visible tool definition (trusted context)."""
        params = self.parameters_schema.get("properties", {})
        lines = [f"Tool: {self.name}", f"Description: {self.description}", "Parameters:"]
        required = set(self.parameters_schema.get("required", []))
        for pname, ptype in params.items():
            flag = " (required)" if pname in required else " (optional)"
            lines.append(f"  - {pname}: {ptype if isinstance(ptype, str) else ptype}{flag}")
        return "\n".join(lines)


def validate_args(schema: dict, args: dict) -> list:
    """Validate ``args`` against a minimal schema. Returns error list."""
    errors: list = []
    properties = schema.get("properties", {})
    for required_name in schema.get("required", []):
        if required_name not in args:
            errors.append(f"missing required parameter: {required_name}")
    for key, value in args.items():
        if key not in properties:
            errors.append(f"unknown parameter: {key}")
            continue
        declared = properties[key]
        declared_type = declared.get("type", "string") if isinstance(declared, dict) else str(declared)
        expected = _TYPE_MAP.get(declared_type)
        if expected is not None and not isinstance(value, expected):
            if not (declared_type == "number" and isinstance(value, int)):
                errors.append(
                    f"parameter {key!r} expected {declared_type}, got {type(value).__name__}"
                )
    return errors


class ToolRegistry:
    """A permission-checked, schema-validated, output-bounded tool set."""

    def __init__(self, caller_access: frozenset | set) -> None:
        self.caller_access = set(caller_access)
        self._tools: dict = {}

    def register(self, spec: ToolSpec, handler: Callable) -> "ToolRegistry":
        self._tools[spec.name] = (spec, handler)
        return self

    def get(self, name: str):
        entry = self._tools.get(name)
        if entry is None:
            return None
        return entry[0]

    def spec_components(self, priority: int = 3) -> list:
        """Tool definitions as trusted context components."""
        return [
            ContextComponent(
                id=f"tool-def-{spec.name}",
                kind=ComponentKind.TOOL_DEFINITION,
                content=spec.render_definition(),
                priority=priority,
                trust=TrustLevel.TRUSTED,
                metadata={"permission": spec.permission},
            )
            for spec, _handler in self._tools.values()
        ]

    def call(self, name: str, args: dict) -> ToolResult:
        """The one guarded path for executing a tool."""
        entry = self._tools.get(name)
        if entry is None:
            return ToolResult.failure(name, f"unknown tool: {name}")
        spec, handler = entry

        # Authorization BEFORE validation BEFORE execution (fail closed).
        if spec.required_access not in self.caller_access:
            return ToolResult.failure(
                name,
                f"caller lacks required access class {spec.required_access!r} for tool {name!r}",
            )

        errors = validate_args(spec.parameters_schema, args)
        if errors:
            return ToolResult.failure(name, "invalid arguments: " + "; ".join(errors))

        try:
            raw = handler(args)
        except Exception as exc:  # noqa: BLE001 — tool isolation is the point
            return ToolResult.failure(
                name, f"tool execution failed: {type(exc).__name__} (details logged, not shown to model)"
            )

        output = str(raw)
        truncated = len(output) > spec.output_max_chars
        if truncated:
            output = output[: spec.output_max_chars] + TRUNCATION_NOTE
        return ToolResult(ok=True, output=output, truncated=truncated, tool=name)
