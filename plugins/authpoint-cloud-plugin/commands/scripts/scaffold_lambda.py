"""
Scaffold script for Folklore hexagonal Lambda functions.
Uses Jinja2 templates.

Usage:
    python scripts/scaffold_lambda.py \\
        --domain cache/resource \\
        --fn saml_resource_cmd_invoker_fn \\
        --module saml_resource \\
        --trigger sqs \\
        --ports repository \\
        --service-name flk-saml-resource-cmd-invoker

Options:
    --domain        Domain path relative to application/src/ (e.g. cache/resource)
    --fn            Lambda function folder name (e.g. saml_resource_cmd_invoker_fn or saml_resource_cmd_invoker)
                    The _fn suffix is added automatically if omitted. --module is derived from --fn by stripping _fn.
    --trigger       Trigger type: sqs | http | ddb_stream
    --ports         One or more ports to scaffold: repository responder invoker publisher producer crypto
    --service-name  Lambda service name used in logging (e.g. flk-saml-resource-cmd-invoker)
    --project-dir   Root of the target project (default: current working directory)
    --force         Overwrite existing files (default: skip existing)
"""

import argparse
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

# ---------------------------------------------------------------------------
# Metadata tables (single source of truth — no logic scattered in templates)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AdapterMeta:
    cls: str
    file: str


ADAPTER_CLASS_MAP: dict[str, AdapterMeta] = {
    "repository": AdapterMeta(cls="DdbRepositoryAdapter", file="ddb_repository"),
    "responder":  AdapterMeta(cls="HttpResponderAdapter",  file="http_responder"),
    "invoker":    AdapterMeta(cls="LambdaInvokerAdapter", file="lambda_invoker"),
    "publisher":  AdapterMeta(cls="SnsPublisher",         file="sns_publisher"),
    "producer":   AdapterMeta(cls="SqsProducer",          file="sqs_producer"),
    "crypto":     AdapterMeta(cls="CommCrypto",            file="comm_crypto"),
}

CONFIG_CLASS_MAP: dict[str, str] = {
    "repository": "DdbRepositoryConfig",
    "responder":  "ResponderConfig",
    "invoker":    "InvokerConfig",
    "publisher":  "SnsPublisherConfig",
    "producer":   "SqsProducerConfig",
    "crypto":     "CryptoConfig",
}

PORT_CLASS_MAP: dict[str, str] = {
    "repository": "Repository",
    "responder":  "ResponderPort",
    "invoker":    "InvokerPort",
    "publisher":  "PublisherPort",
    "producer":   "ProducerPort",
    "crypto":     "CryptoPort",
}

ADAPTER_NEEDS_PARSER: set[str] = {"repository", "invoker", "publisher", "producer", "crypto"}

TRIGGER_APP_TEMPLATE: dict[str, str] = {
    "sqs":        "app_sqs.py.j2",
    "http":       "app_http.py.j2",
    "ddb_stream": "app_ddb_stream.py.j2",
}

VALID_TRIGGERS = set(TRIGGER_APP_TEMPLATE.keys())
VALID_PORTS = set(ADAPTER_CLASS_MAP.keys())

# ---------------------------------------------------------------------------
# Jinja2 environment
# ---------------------------------------------------------------------------

TEMPLATES_DIR = Path(__file__).parent / "templates" / "src"


def _make_jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _render(env: Environment, template_name: str, ctx: dict) -> str:
    return env.get_template(template_name).render(**ctx)


# ---------------------------------------------------------------------------
# File writing
# ---------------------------------------------------------------------------

def _write_file(path: Path, content: str, force: bool, project_dir: Path) -> None:
    if path.exists() and not force:
        print(f"  [SKIP]  {path.relative_to(project_dir)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  [OK]    {path.relative_to(project_dir)}")


def _write_init(directory: Path, force: bool, project_dir: Path) -> None:
    _write_file(directory / "__init__.py", "", force, project_dir)


# ---------------------------------------------------------------------------
# Scaffold
# ---------------------------------------------------------------------------

def scaffold(
    domain: str,
    fn: str,
    module: str,
    trigger: str,
    ports: list[str],
    service_name: str,
    force: bool,
    project_dir: Path,
) -> None:
    fn_dir = project_dir / "application" / "src" / domain / fn
    mod_dir = fn_dir / module

    print(f"\nScaffolding: {fn_dir.relative_to(project_dir)}")
    print(f"  trigger : {trigger}")
    print(f"  ports   : {ports or ['(none)']}")
    print()

    env = _make_jinja_env()

    base_ctx = dict(
        module=module,
        service_name=service_name,
        trigger=trigger,
        ports=ports,
        adapter_class_map=ADAPTER_CLASS_MAP,
        config_class_map=CONFIG_CLASS_MAP,
        port_class_map=PORT_CLASS_MAP,
        adapter_needs_parser=ADAPTER_NEEDS_PARSER,
    )

    # __init__.py for every intermediate domain directory and fn_dir
    src_dir = project_dir / "application" / "src"
    current = src_dir
    for part in list(Path(domain).parts) + [fn]:
        current = current / part
        _write_init(current, force, project_dir)

    # app.py
    app_tpl = TRIGGER_APP_TEMPLATE[trigger]
    _write_file(fn_dir / "app.py", _render(env, app_tpl, base_ctx), force, project_dir)

    # <module>/__init__.py
    _write_init(mod_dir, force, project_dir)

    # configuration.py
    _write_file(
        mod_dir / "configuration.py",
        _render(env, "configuration.py.j2", base_ctx),
        force,
        project_dir,
    )

    # domain/service.py
    _write_init(mod_dir / "domain", force, project_dir)
    _write_file(
        mod_dir / "domain" / "service.py",
        _render(env, "service.py.j2", base_ctx),
        force,
        project_dir,
    )

    if not ports:
        print("\nDone. Review TODOs in generated files before running the SDD pipeline.")
        return

    # port/<port>.py
    _write_init(mod_dir / "port", force, project_dir)
    for port in ports:
        if port in PORT_CLASS_MAP:
            _write_file(
                mod_dir / "port" / f"{port}.py",
                _render(env, "port.py.j2", {**base_ctx, "port": port}),
                force,
                project_dir,
            )

    # adapter/<adapter>.py
    _write_init(mod_dir / "adapter", force, project_dir)
    for port in ports:
        if port in ADAPTER_CLASS_MAP:
            meta = ADAPTER_CLASS_MAP[port]
            _write_file(
                mod_dir / "adapter" / f"{meta.file}.py",
                _render(env, "adapter.py.j2", {**base_ctx, "port": port}),
                force,
                project_dir,
            )

    print("\nDone. Review TODOs in generated files before running the SDD pipeline.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a Folklore hexagonal Lambda function.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--domain", required=True,
                        help="Domain path relative to application/src/ (e.g. cache/resource)")
    parser.add_argument("--fn", required=True,
                        help="Lambda function folder name (e.g. saml_resource_cmd_invoker_fn or saml_resource_cmd_invoker — _fn suffix added automatically)")
    parser.add_argument("--trigger", required=True, choices=sorted(VALID_TRIGGERS),
                        help="Trigger type: sqs | http | ddb_stream")
    parser.add_argument("--ports", nargs="*", default=[], choices=sorted(VALID_PORTS),
                        help="Ports to scaffold (space-separated)")
    parser.add_argument("--service-name", required=True,
                        help="Lambda service name used in logging (e.g. flk-saml-resource-cmd-invoker)")
    parser.add_argument("--project-dir", default=None,
                        help="Root of the target project (default: current working directory)")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing files")

    args = parser.parse_args()
    project_dir = Path(args.project_dir).resolve() if args.project_dir else Path.cwd()

    fn = args.fn if args.fn.endswith("_fn") else f"{args.fn}_fn"
    module = fn[:-3]  # strip trailing _fn

    scaffold(
        domain=args.domain,
        fn=fn,
        module=module,
        trigger=args.trigger,
        ports=args.ports,
        service_name=args.service_name,
        force=args.force,
        project_dir=project_dir,
    )


if __name__ == "__main__":
    main()
