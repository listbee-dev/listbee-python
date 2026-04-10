#!/usr/bin/env python3
"""Spec drift validator — detects drift between openapi.json and SDK code.

Reads the OpenAPI spec (local file or fetched from URL), scans src/listbee/
for Pydantic models and resource methods. Reports missing, stale, and extra items.

Exit 0 = clean, Exit 1 = drift detected.

Usage:
    uv run python scripts/validate_spec.py [--spec path/to/openapi.json] [--url https://...]
"""

from __future__ import annotations

import ast
import json
import sys
import tempfile
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SPEC = REPO_ROOT / "openapi.json"
SDK_ROOT = REPO_ROOT / "src" / "listbee"
RESOURCES_DIR = SDK_ROOT / "resources"
TYPES_DIR = SDK_ROOT / "types"

LIVE_SPEC_URL = "https://api.listbee.so/openapi.json"

# Operations that are handled by the signup resource (not missing)
SIGNUP_OPS = {"send_otp", "verify_otp"}

# Schemas to skip for field comparison (not response models)
SKIP_SCHEMAS = {
    "HTTPValidationError",
    "ValidationError",
    "ProblemDetail",
    "Body_upload_file",
    # Request-only schemas
    "ListingCreateRequest",
    "ListingUpdateRequest",
    "OrderShipRequest",
    "WebhookCreateRequest",
    "WebhookUpdateRequest",
    "CheckoutFieldInput",
    "DeliverableInput",
    # Enums / non-model schemas
    "CreateAccountRequest",
    "CreateApiKeyRequest",
    "CreateListingRequest",
    "CreateWebhookRequest",
    "UpdateAccountRequest",
    "UpdateListingRequest",
    "UpdateWebhookRequest",
    "DeliverOrderRequest",
    "DeliverableInputRequest",
    "SetDeliverablesRequest",
    "ShipOrderRequest",
    "VerifyOtpRequest",
}


def fetch_spec_to_tempfile(url: str) -> Path:
    """Fetch OpenAPI spec from URL and write to a temp file. Returns temp file path."""
    print(f"Fetching spec from {url} ...")
    with urllib.request.urlopen(url) as response:  # noqa: S310
        data = response.read()
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp.write(data)
        tmp.flush()
        return Path(tmp.name)


def load_spec(spec_path: Path) -> dict:
    if not spec_path.exists():
        print(f"ERROR: OpenAPI spec not found at {spec_path}", file=sys.stderr)
        print("Pass --spec path/to/openapi.json or --url to fetch from remote.", file=sys.stderr)
        sys.exit(1)
    return json.loads(spec_path.read_text())


def extract_spec_operations(spec: dict) -> dict[str, dict]:
    """Extract all operations from OpenAPI spec: {operation_id: {method, path}}."""
    ops: dict[str, dict] = {}
    for path, methods in (spec.get("paths") or {}).items():
        # Skip internal console routes — session-authenticated, not part of public API
        if path.startswith("/console"):
            continue
        for method, op in methods.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            op_id = op.get("operationId")
            if op_id:
                ops[op_id] = {"method": method.upper(), "path": path}
    return ops


def extract_spec_schemas(spec: dict) -> dict[str, dict]:
    """Extract response schemas: {schema_name: {fields: {name: type}}}."""
    schemas: dict[str, dict] = {}
    for name, schema in (spec.get("components", {}).get("schemas") or {}).items():
        if name in ("HTTPValidationError", "ValidationError", "ProblemDetail", "Body_upload_file"):
            continue
        fields: dict[str, str] = {}
        for prop_name, prop_schema in (schema.get("properties") or {}).items():
            fields[prop_name] = prop_schema.get("type", "unknown")
        schemas[name] = {"fields": fields, "required": schema.get("required", [])}
    return schemas


def scan_resource_methods(resources_dir: Path) -> dict[str, list[dict]]:
    """Scan resource files for method definitions using AST.

    Returns: {filename: [{name, is_async, args}]}
    """
    results: dict[str, list[dict]] = {}
    for py_file in sorted(resources_dir.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        try:
            tree = ast.parse(py_file.read_text())
        except SyntaxError:
            continue

        methods: list[dict] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                        if item.name.startswith("_"):
                            continue
                        methods.append(
                            {
                                "name": item.name,
                                "class": node.name,
                                "is_async": isinstance(item, ast.AsyncFunctionDef),
                                "line": item.lineno,
                            }
                        )
        if methods:
            results[py_file.stem] = methods
    return results


def scan_pydantic_models(types_dir: Path) -> dict[str, list[str]]:
    """Scan type files for Pydantic model class definitions.

    Returns: {filename: [ClassName, ...]}
    """
    results: dict[str, list[str]] = {}
    for py_file in sorted(types_dir.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        try:
            tree = ast.parse(py_file.read_text())
        except SyntaxError:
            continue

        classes: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it inherits from BaseModel
                for base in node.bases:
                    base_name = ""
                    if isinstance(base, ast.Name):
                        base_name = base.id
                    elif isinstance(base, ast.Attribute):
                        base_name = base.attr
                    if base_name == "BaseModel":
                        classes.append(node.name)
                        break
        if classes:
            results[py_file.stem] = classes
    return results


def scan_model_fields(types_dir: Path) -> dict[str, set[str]]:
    """Scan type files for Pydantic model field names using AST.

    Returns: {ClassName: set[field_name]}  (only classes that inherit from BaseModel)
    """
    results: dict[str, set[str]] = {}
    for py_file in sorted(types_dir.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        try:
            tree = ast.parse(py_file.read_text())
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            # Only Pydantic BaseModel subclasses
            is_model = False
            for base in node.bases:
                base_name = ""
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr
                if base_name == "BaseModel":
                    is_model = True
                    break
            if not is_model:
                continue

            fields: set[str] = set()
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    fields.add(item.target.id)
            if fields:
                results[node.name] = fields
    return results


def compare_fields(
    spec: dict,
    model_fields: dict[str, set[str]],
) -> list[dict]:
    """Compare OpenAPI schema properties against Pydantic model fields.

    Returns a list of issue dicts with keys: kind, schema, field, message.
    """
    issues: list[dict] = []
    schemas = spec.get("components", {}).get("schemas") or {}

    for schema_name, schema_def in schemas.items():
        # Skip internal / request-only schemas
        if schema_name in SKIP_SCHEMAS:
            continue
        if schema_name.endswith("Request") or schema_name.endswith("Input"):
            continue
        # Only compare schemas that have properties (i.e. object schemas)
        spec_props = set(schema_def.get("properties") or {})
        if not spec_props:
            continue
        # Match schema name to model class name (often identical)
        if schema_name not in model_fields:
            continue  # No matching model — not a field drift issue

        model_props = model_fields[schema_name]

        for field in sorted(spec_props - model_props):
            issues.append(
                {
                    "kind": "MISSING FIELD",
                    "schema": schema_name,
                    "field": field,
                    "message": f'Schema "{schema_name}" has field "{field}" not found in Python model.',
                }
            )

        for field in sorted(model_props - spec_props):
            issues.append(
                {
                    "kind": "EXTRA FIELD",
                    "schema": schema_name,
                    "field": field,
                    "message": f'Python model "{schema_name}" has field "{field}" not in OpenAPI schema.',
                }
            )

    return issues


# Explicit overrides for operation IDs that don't follow standard patterns
OP_ID_OVERRIDES: dict[str, str] = {
    "deliver_order": "deliver",
    "start_stripe_connect": "connect",
    "disconnect_stripe": "disconnect",
    "bootstrap_start": "start",
    "bootstrap_verify": "verify",
    "bootstrap_store": "create_store",
}

# Multi-word resource names (operation ID resource part → SDK resource file stem)
RESOURCE_ALIASES: dict[str, str] = {}


def op_id_to_method_name(op_id: str) -> str:
    """Convert operation_id to expected SDK method name.

    e.g. list_customers -> list, get_customer -> get, create_listing -> create,
    publish_listing -> publish, refund_order -> refund, retry_webhook_event -> retry_event
    """
    if op_id in OP_ID_OVERRIDES:
        return OP_ID_OVERRIDES[op_id]

    parts = op_id.split("_")
    if len(parts) <= 2:
        return parts[0]  # list, get, create, delete, etc.

    # Handle multi-word resource names: list_api_keys -> list
    for alias in RESOURCE_ALIASES:
        if op_id.endswith(f"_{alias}") or f"_{alias}_" in op_id:
            return parts[0]

    # e.g. retry_webhook_event -> retry_event, list_webhook_events -> list_events
    return "_".join(parts[0:1] + parts[2:]) if len(parts) == 3 else parts[0]


def main() -> None:
    spec_path: Path | None = None

    # --url: fetch from remote
    if "--url" in sys.argv:
        idx = sys.argv.index("--url")
        if idx + 1 < len(sys.argv):
            spec_path = fetch_spec_to_tempfile(sys.argv[idx + 1])
        else:
            print("ERROR: --url requires a URL argument", file=sys.stderr)
            sys.exit(1)

    # --spec: explicit local path
    if spec_path is None and "--spec" in sys.argv:
        idx = sys.argv.index("--spec")
        if idx + 1 < len(sys.argv):
            spec_path = Path(sys.argv[idx + 1])

    # Default: try local openapi.json, else fetch from live API
    if spec_path is None:
        spec_path = DEFAULT_SPEC if DEFAULT_SPEC.exists() else fetch_spec_to_tempfile(LIVE_SPEC_URL)

    spec = load_spec(spec_path)
    spec_ops = extract_spec_operations(spec)
    sdk_methods = scan_resource_methods(RESOURCES_DIR)
    sdk_models = scan_pydantic_models(TYPES_DIR)
    model_fields = scan_model_fields(TYPES_DIR)

    # Build flat set of all SDK method names (sync only — async mirrors sync)
    sdk_method_set: set[str] = set()
    for _file, methods in sdk_methods.items():
        for m in methods:
            if not m["is_async"]:
                sdk_method_set.add(f"{_file}.{m['name']}")

    issues: list[dict] = []

    # Check: operations in spec but no matching SDK method
    for op_id, op_info in spec_ops.items():
        if op_id in SIGNUP_OPS:
            continue  # Handled by signup resource

        # Try to find matching method
        found = False
        for _file, methods in sdk_methods.items():
            for m in methods:
                if m["is_async"]:
                    continue
                # Check if method name matches expected
                if m["name"] == op_id_to_method_name(op_id):
                    found = True
                    break
                # Also check direct name match
                if m["name"] == op_id:
                    found = True
                    break
            if found:
                break

        if not found:
            issues.append(
                {
                    "kind": "MISSING METHOD",
                    "message": f'Operation "{op_id}" ({op_info["method"]} {op_info["path"]}) has no matching SDK method.',
                }
            )

    # Field-level drift: compare OpenAPI schema properties against Pydantic models
    issues.extend(compare_fields(spec, model_fields))

    # Report
    total_methods = sum(1 for _f, ms in sdk_methods.items() for m in ms if not m["is_async"])
    total_models = sum(len(cs) for cs in sdk_models.values())
    total_model_classes = len(model_fields)

    print()
    print("=== Spec Drift Check ===")
    print(f"Spec operations:  {len(spec_ops)}")
    print(f"SDK methods:      {total_methods}")
    print(f"SDK models:       {total_models}")
    print(f"Resource files:   {len(sdk_methods)}")
    print(f"Model classes:    {total_model_classes}")
    print()

    if not issues:
        print("No drift detected.")
        print()
        sys.exit(0)

    # Group by kind
    for kind in ("MISSING METHOD", "STALE METHOD", "MISSING MODEL", "MISSING FIELD", "EXTRA FIELD"):
        group = [i for i in issues if i["kind"] == kind]
        if not group:
            continue
        print(f"--- {kind} ({len(group)}) ---")
        for issue in group:
            print(f"  {issue['message']}")
        print()

    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue["kind"]] = counts.get(issue["kind"], 0) + 1
    summary = ", ".join(f"{v} {k}" for k, v in counts.items())
    print(f"DRIFT DETECTED: {len(issues)} issue(s) — {summary}")
    print()
    sys.exit(1)


if __name__ == "__main__":
    main()
