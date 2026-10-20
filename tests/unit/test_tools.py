"""Tests for tool registry: permissions, validation, bounded outputs."""

import unittest

from context_engineering.context import ComponentKind, TrustLevel
from context_engineering.tools import ToolRegistry, ToolResult, ToolSpec, validate_args


def calendar_spec():
    return ToolSpec(
        name="calendar_check",
        description="Check the employee calendar for availability. Use for scheduling questions only.",
        parameters_schema={
            "properties": {
                "query": {"type": "string"},
                "date_range": {"type": "string"},
                "verbose": {"type": "boolean"},
            },
            "required": ["query", "date_range"],
        },
        required_access="internal",
        permission="calendar.read",
        output_max_chars=200,
    )


class TestValidateArgs(unittest.TestCase):
    def test_missing_required_reported(self):
        errors = validate_args(calendar_spec().parameters_schema, {"query": "x"})
        self.assertTrue(any("date_range" in e for e in errors))

    def test_type_mismatch_reported(self):
        errors = validate_args(
            calendar_spec().parameters_schema,
            {"query": "ok", "date_range": "ok", "verbose": "not-a-bool"},
        )
        self.assertTrue(any("verbose" in e for e in errors))

    def test_unknown_parameter_reported(self):
        errors = validate_args(
            calendar_spec().parameters_schema, {"query": "a", "date_range": "b", "extra": 1}
        )
        self.assertTrue(any("extra" in e for e in errors))

    def test_valid_args_pass(self):
        self.assertEqual(
            validate_args(
                calendar_spec().parameters_schema, {"query": "policy review", "date_range": "this week"}
            ),
            [],
        )


class TestToolRegistry(unittest.TestCase):
    def _registry(self, access=("internal",)):
        registry = ToolRegistry(caller_access=frozenset(access))
        registry.register(calendar_spec(), lambda args: f"Availability for {args['query']}.")
        return registry

    def test_unknown_tool_fails_structured(self):
        result = self._registry().call("nonexistent", {})
        self.assertFalse(result.ok)
        self.assertIn("unknown tool", result.error)

    def test_unauthorized_caller_fails_before_validation(self):
        registry = self._registry(access=("public",))
        result = registry.call("calendar_check", {"query": "x", "date_range": "y"})
        self.assertFalse(result.ok)
        self.assertIn("lacks required access", result.error)

    def test_invalid_args_fail_with_reasons(self):
        result = self._registry().call("calendar_check", {})
        self.assertFalse(result.ok)
        self.assertIn("invalid arguments", result.error)
        self.assertIn("query", result.error)

    def test_handler_exception_isolated_not_leaked(self):
        registry = self._registry()
        registry.register(
            ToolSpec(
                name="explode",
                description="Always raises.",
                parameters_schema={"properties": {}, "required": []},
            ),
            lambda args: (_ for _ in ()).throw(RuntimeError("secret stack detail")),
        )
        result = registry.call("explode", {})
        self.assertFalse(result.ok)
        self.assertNotIn("secret stack detail", result.error)  # never into context

    def test_output_truncation_flagged(self):
        registry = self._registry()
        registry.register(
            ToolSpec(
                name="chatty",
                description="Returns a lot.",
                parameters_schema={"properties": {}, "required": []},
                output_max_chars=50,
            ),
            lambda args: "x" * 500,
        )
        result = registry.call("chatty", {})
        self.assertTrue(result.ok)
        self.assertTrue(result.truncated)
        from context_engineering.tools import TRUNCATION_NOTE

        self.assertLessEqual(len(result.output), 50 + len(TRUNCATION_NOTE))  # cap + marker
        self.assertIn("[output truncated", result.output)

    def test_tool_definitions_are_trusted_components(self):
        components = self._registry().spec_components()
        self.assertEqual(len(components), 1)
        comp = components[0]
        self.assertEqual(comp.kind, ComponentKind.TOOL_DEFINITION)
        self.assertEqual(comp.trust, TrustLevel.TRUSTED)
        self.assertIn("calendar_check", comp.content)


if __name__ == "__main__":
    unittest.main()
