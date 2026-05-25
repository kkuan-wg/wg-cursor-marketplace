#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp[cli]"]
# ///
"""
AuthPoint Spec MCP Server

Exposes the ai-tool-authpoint-spec repository files as MCP tools,
allowing agents in implementation repos to query specs by domain/name.

Domains from all four namespace roots are merged into a single flat namespace:
  ssot/legacy/domain
  ssot/folklore/domain
  ssot/integration/domain
  ssot/external/domain

Requires the AUTHPOINT_SPEC_REPO environment variable to point to the
root of a local clone of the ai-tool-authpoint-spec repository.
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _get_repo_root() -> Path:
    raw = os.environ.get("AUTHPOINT_SPEC_REPO", "")
    if not raw:
        raise RuntimeError(
            "AUTHPOINT_SPEC_REPO environment variable is not set. "
            "Point it to the root of your local ai-tool-authpoint-spec clone.\n\n"
            "  Windows (PowerShell profile):\n"
            '    $env:AUTHPOINT_SPEC_REPO = "C:\\Users\\<you>\\Projects\\ai-tool-authpoint-spec"\n'
            "    # To persist: add the line above to $PROFILE\n\n"
            "  macOS / Linux (~/.zshrc or ~/.bashrc):\n"
            '    export AUTHPOINT_SPEC_REPO="$HOME/Projects/ai-tool-authpoint-spec"\n'
            "    # Then run: source ~/.zshrc"
        )
    path = Path(raw)
    if not path.is_dir():
        raise RuntimeError(
            f"AUTHPOINT_SPEC_REPO='{raw}' does not exist or is not a directory. "
            "Check that the path is correct and the repository has been cloned."
        )
    return path


_REPO_ROOT = _get_repo_root()

# Each entry is (namespace_label, path).  All four namespace roots are indexed.
SPEC_ROOTS: list[tuple[str, Path]] = [
    ("legacy",      _REPO_ROOT / "ssot" / "legacy"      / "domain"),
    ("folklore",    _REPO_ROOT / "ssot" / "folklore"     / "domain"),
    ("integration", _REPO_ROOT / "ssot" / "integration"  / "domain"),
    ("external",    _REPO_ROOT / "ssot" / "external"     / "domain"),
]

# Folder-name aliases to handle inconsistencies in the SSOT repo:
#   specs/ vs spec/  |  api-contract/ vs api_contract/  |  examples/ vs example/
_FOLDER_ALIASES: dict[str, list[str]] = {
    "specs":        ["specs", "spec"],
    "api-contract": ["api-contract", "api_contract"],
    "event":        ["event", "events"],
    "examples":     ["examples", "example"],
}

_last_pull_status: str = "refresh() not called yet"

mcp = FastMCP("ai-tool-authpoint-spec")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _git_pull() -> str:
    if not (_REPO_ROOT / ".git").exists():
        msg = f"Not a git repository, skipping pull: {_REPO_ROOT}"
        logger.warning(msg)
        return msg
    try:
        result = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            msg = result.stdout.strip() or "Already up to date."
            logger.info("git pull: %s", msg)
            return msg
        msg = f"git pull failed: {result.stderr.strip()}"
        logger.warning(msg)
        return msg
    except subprocess.TimeoutExpired:
        msg = "git pull timed out, continuing with local files."
        logger.warning(msg)
        return msg
    except FileNotFoundError:
        msg = "git not found in PATH, skipping pull."
        logger.warning(msg)
        return msg


def _available_roots() -> list[tuple[str, Path]]:
    return [(ns, p) for ns, p in SPEC_ROOTS if p.exists()]


def _resolve_subdir(domain_path: Path, logical_name: str) -> Path:
    """Return the first existing alias for a logical subfolder name.

    Falls back to ``domain_path / logical_name`` when no alias matches,
    so callers can check ``path.exists()`` themselves.
    """
    for alias in _FOLDER_ALIASES.get(logical_name, [logical_name]):
        candidate = domain_path / alias
        if candidate.exists():
            return candidate
    return domain_path / logical_name


def _resolve_domain(domain: str) -> Path:
    for _ns, root in _available_roots():
        candidate = root / domain
        if candidate.exists():
            return candidate
    available = _all_domains()
    raise FileNotFoundError(
        f"Domain '{domain}' not found in any spec root. Available: {available}"
    )


def _resolve_domain_with_ns(domain: str) -> tuple[str, Path]:
    """Return (namespace, domain_path) for the given domain name."""
    for ns, root in _available_roots():
        candidate = root / domain
        if candidate.exists():
            return ns, candidate
    available = _all_domains()
    raise FileNotFoundError(
        f"Domain '{domain}' not found in any spec root. Available: {available}"
    )


def _all_domains() -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for _ns, root in _available_roots():
        for d in sorted(root.iterdir()):
            if d.is_dir() and d.name not in seen:
                seen.add(d.name)
                result.append(d.name)
    return sorted(result)


def _read_file(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


_IGNORED_FILES = {".gitkeep", ".DS_Store", "Thumbs.db"}


def _build_tree(path: Path) -> dict:
    result: dict = {}
    files = sorted(
        f.name for f in path.iterdir()
        if f.is_file() and f.name not in _IGNORED_FILES and not f.name.startswith(".")
    )
    if files:
        result["files"] = files
    for subdir in sorted(d for d in path.iterdir() if d.is_dir()):
        subtree = _build_tree(subdir)
        result[subdir.name] = subtree
    return result


def _find_file(directory: Path, name: str) -> Optional[Path]:
    if "/" in name:
        parts = Path(name)
        candidate = directory / parts
        if candidate.exists() and candidate.is_file():
            return candidate
        for ext in (".yaml", ".yml", ".md", ".json"):
            candidate = directory / f"{name}{ext}"
            if candidate.exists():
                return candidate
        return None

    for ext in (".yaml", ".yml", ".md", ".json"):
        candidate = directory / f"{name}{ext}"
        if candidate.exists():
            return candidate
    subdir_spec = directory / name / "spec.md"
    if subdir_spec.exists():
        return subdir_spec
    return None


def _list_directory(domain_path: Path, logical_subdir: str) -> dict:
    path = _resolve_subdir(domain_path, logical_subdir)
    if not path.exists():
        return {}
    return _build_tree(path)


def _flat_spec_files(domain_path: Path) -> list[dict]:
    """Walk specs/ and return a flat list of spec entries."""
    specs_dir = _resolve_subdir(domain_path, "specs")
    if not specs_dir.exists():
        return []
    entries: list[dict] = []
    for item in sorted(specs_dir.rglob("*")):
        if item.is_file() and item.name not in _IGNORED_FILES and not item.name.startswith("."):
            rel = item.relative_to(specs_dir)
            # Use the parent folder name as the spec id when the file is spec.md
            spec_id = rel.parent.name if item.name == "spec.md" and rel.parent != Path(".") else rel.stem
            entries.append({
                "id": spec_id,
                "file": item.name,
                "path": str(rel).replace("\\", "/"),
            })
    return entries


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def refresh() -> str:
    """
    Pull the latest changes from the remote ai-tool-authpoint-spec repository.
    Call this before starting work to ensure specs are up to date.
    """
    global _last_pull_status
    _last_pull_status = _git_pull()
    return _last_pull_status


@mcp.tool()
def get_pull_status() -> str:
    """
    Returns the result of the last git pull attempt.

    Useful to check whether the agent is working with up-to-date specs
    or a local cache (e.g. pull failed due to conflict or no network).
    """
    return _last_pull_status


@mcp.tool()
def list_domains() -> list[str]:
    """List all available domain names across all namespace roots of the ai-tool-authpoint-spec repository."""
    return _all_domains()


@mcp.tool()
def list_domains_with_namespaces() -> list[dict]:
    """
    List all domains together with their namespace (legacy, folklore, integration, external).

    Returns a list of objects like {"namespace": "folklore", "domain": "saml"}.
    Prefer this over list_domains when you need to understand where a domain lives.
    """
    result: list[dict] = []
    seen: set[str] = set()
    for ns, root in _available_roots():
        if not root.exists():
            continue
        for d in sorted(root.iterdir()):
            if d.is_dir() and d.name not in seen:
                seen.add(d.name)
                result.append({"namespace": ns, "domain": d.name})
    return sorted(result, key=lambda x: (x["domain"], x["namespace"]))


@mcp.tool()
def list_specs(domain: str) -> dict:
    """
    List all spec files and directories available for a given domain.

    Args:
        domain: Domain name (e.g. 'oidc', 'saml', 'wif-provisioning')
    """
    return _list_directory(_resolve_domain(domain), "specs")


@mcp.tool()
def list_all_specs(domain: str) -> list[dict]:
    """
    Return a flat list of all spec files for a domain, including their spec ID and relative path.

    Each entry has the form:
      {"id": "aaas-30040-flk-saml-user-cache", "file": "spec.md", "path": "aaas-30040-.../spec.md"}

    Use this instead of list_specs when you need to pick a specific spec to read without
    navigating the nested tree manually.

    Args:
        domain: Domain name (e.g. 'saml', 'core', 'wif-provisioning')
    """
    return _flat_spec_files(_resolve_domain(domain))


@mcp.tool()
def list_api_contracts(domain: str) -> dict:
    """
    List all API contract files available for a given domain.

    Args:
        domain: Domain name (e.g. 'oidc')
    """
    return _list_directory(_resolve_domain(domain), "api-contract")


@mcp.tool()
def list_events(domain: str) -> dict:
    """
    List all event files and directories available for a given domain.

    Args:
        domain: Domain name (e.g. 'saml', 'cache', 'wif-provisioning')
    """
    return _list_directory(_resolve_domain(domain), "event")


@mcp.tool()
def list_event_schemas(domain: str) -> list[str]:
    """
    List only the AsyncAPI schema files (*.asyncapi.yaml) in the event/ directory,
    excluding the examples/ subfolder.

    Use this when you want to discover available event types without the noise of
    example JSON files.

    Args:
        domain: Domain name (e.g. 'saml', 'cache', 'wif-provisioning')
    """
    event_dir = _resolve_subdir(_resolve_domain(domain), "event")
    if not event_dir.exists():
        return []
    return sorted(
        f.name
        for f in event_dir.iterdir()
        if f.is_file() and f.suffix in (".yaml", ".yml") and "asyncapi" in f.name
    )


@mcp.tool()
def list_database_models(domain: str) -> dict:
    """
    List all database model files available for a given domain.

    Args:
        domain: Domain name (e.g. 'saml', 'core', 'wif-provisioning')
    """
    return _list_directory(_resolve_domain(domain), "database-model")


@mcp.tool()
def get_spec(domain: str, spec_name: str) -> str:
    """
    Get the content of a specific SDD for a domain.

    Args:
        domain: Domain name (e.g. 'saml', 'core')
        spec_name: Spec file name without extension, or a folder name whose spec.md will be read
                   (e.g. 'aaas-30040-flk-saml-user-cache' or 'authorize-flow')
    """
    specs_dir = _resolve_subdir(_resolve_domain(domain), "specs")
    path = _find_file(specs_dir, spec_name)
    if path is None:
        available = _build_tree(specs_dir) if specs_dir.exists() else {}
        return f"Spec '{spec_name}' not found in domain '{domain}'. Available: {available}"
    return _read_file(path)


@mcp.tool()
def get_api_contract(domain: str, api_name: str) -> str:
    """
    Get the content of an API contract (OpenAPI/YAML) for a domain.

    Args:
        domain: Domain name (e.g. 'oidc')
        api_name: Contract file name without extension (e.g. 'openapi_oidc_authx' or 'openapi')
    """
    contracts_dir = _resolve_subdir(_resolve_domain(domain), "api-contract")
    path = _find_file(contracts_dir, api_name)
    if path is None:
        available = _build_tree(contracts_dir) if contracts_dir.exists() else {}
        return f"API contract '{api_name}' not found in domain '{domain}'. Available: {available}"
    return _read_file(path)


@mcp.tool()
def get_event_schema(domain: str, schema_name: str = "schema") -> str:
    """
    Get the AsyncAPI event schema file for a domain.

    Args:
        domain: Domain name (e.g. 'saml', 'cache', 'wif-provisioning')
        schema_name: Schema file name without extension (e.g. 'saml-transaction-created' or 'schema').
                     Use list_event_schemas(domain) to discover available schema file names.
    """
    events_dir = _resolve_subdir(_resolve_domain(domain), "event")
    path = _find_file(events_dir, schema_name)
    if path is None:
        available = _build_tree(events_dir) if events_dir.exists() else {}
        return f"Event schema '{schema_name}' not found in domain '{domain}'. Available: {available}"
    return _read_file(path)


@mcp.tool()
def get_events(domain: str, schema_name: str = "schema") -> str:
    """
    Deprecated alias for get_event_schema(). Use get_event_schema() instead.

    Get the AsyncAPI event schema file for a domain.

    Args:
        domain: Domain name (e.g. 'saml', 'cache')
        schema_name: Schema file name without extension (default: 'schema')
    """
    return get_event_schema(domain, schema_name)


@mcp.tool()
def get_event_example(domain: str, event_name: str) -> str:
    """
    Get a JSON example for a specific event type.

    Args:
        domain: Domain name (e.g. 'saml', 'core', 'wif-provisioning')
        event_name: Event example file name without extension (e.g. 'saml_transaction_created')
    """
    event_dir = _resolve_subdir(_resolve_domain(domain), "event")
    examples_dir = _resolve_subdir(event_dir, "examples")
    path = _find_file(examples_dir, event_name)
    if path is None:
        available = _build_tree(examples_dir) if examples_dir.exists() else {}
        return f"Event example '{event_name}' not found in domain '{domain}'. Available: {available}"
    return _read_file(path)


@mcp.tool()
def get_database_model(domain: str, model_name: str) -> str:
    """
    Get the database model definition for a specific entity.

    Args:
        domain: Domain name (e.g. 'saml', 'core', 'wif-provisioning')
        model_name: Model file name without extension (e.g. 'transaction' or 'passkey_credentials')
    """
    models_dir = _resolve_subdir(_resolve_domain(domain), "database-model")
    path = _find_file(models_dir, model_name)
    if path is None:
        available = _build_tree(models_dir) if models_dir.exists() else {}
        return f"Database model '{model_name}' not found in domain '{domain}'. Available: {available}"
    return _read_file(path)


@mcp.tool()
def get_error_codes(domain: str) -> str:
    """
    Get the error codes definition for a domain.

    Args:
        domain: Domain name (e.g. 'saml', 'oidc')
    """
    path = _resolve_domain(domain) / "error-codes.md"
    if not path.exists():
        return f"No error-codes.md found for domain '{domain}'."
    return _read_file(path)


@mcp.tool()
def get_sequence_diagram(domain: str, diagram_name: str) -> str:
    """
    Get a sequence diagram for a domain.

    Args:
        domain: Domain name (e.g. 'saml', 'oidc')
        diagram_name: Diagram file name without extension
    """
    diagrams_dir = _resolve_domain(domain) / "sequence-diagram"
    path = _find_file(diagrams_dir, diagram_name)
    if path is None:
        available = _build_tree(diagrams_dir) if diagrams_dir.exists() else {}
        return f"Sequence diagram '{diagram_name}' not found in domain '{domain}'. Available: {available}"
    return _read_file(path)


@mcp.tool()
def get_domain_summary(domain: str) -> dict:
    """
    Returns a full recursive inventory of all files and directories for a domain.

    Use this at the start of any task to discover what artifacts exist before
    deciding which tools to call.

    Args:
        domain: Domain name (e.g. 'saml', 'oidc', 'wif-provisioning')
    """
    try:
        ns, domain_path = _resolve_domain_with_ns(domain)
    except FileNotFoundError as e:
        return {"error": str(e)}
    return {"domain": domain, "namespace": ns, **_build_tree(domain_path)}


@mcp.tool()
def search_specs(keyword: str, max_results: int = 10) -> list[dict]:
    """
    Search all spec files across all domains and namespaces for a keyword (case-insensitive).

    Returns up to max_results matches. Each result has:
      {"namespace": ..., "domain": ..., "spec_path": ..., "excerpt": ...}

    Use list_domains + get_spec to retrieve the full content of a matching spec.

    Args:
        keyword: Case-insensitive search term (e.g. 'passkey', 'authorize', 'SAML transaction')
        max_results: Maximum number of results to return (default: 10)
    """
    keyword_lower = keyword.lower()
    results: list[dict] = []

    for ns, root in _available_roots():
        if not root.exists():
            continue
        for domain_dir in sorted(root.iterdir()):
            if not domain_dir.is_dir():
                continue
            specs_dir = _resolve_subdir(domain_dir, "specs")
            if not specs_dir.exists():
                continue
            for spec_file in sorted(specs_dir.rglob("*.md")):
                if spec_file.name.startswith("."):
                    continue
                try:
                    content = spec_file.read_text(encoding="utf-8")
                except OSError:
                    continue
                if keyword_lower not in content.lower():
                    continue
                # Build a short excerpt around the first match
                idx = content.lower().find(keyword_lower)
                start = max(0, idx - 60)
                end = min(len(content), idx + len(keyword) + 60)
                excerpt = content[start:end].replace("\n", " ").strip()
                if start > 0:
                    excerpt = "…" + excerpt
                if end < len(content):
                    excerpt = excerpt + "…"

                rel_path = spec_file.relative_to(specs_dir)
                results.append({
                    "namespace": ns,
                    "domain": domain_dir.name,
                    "spec_path": str(rel_path).replace("\\", "/"),
                    "excerpt": excerpt,
                })
                if len(results) >= max_results:
                    return results
    return results


def main() -> None:
    global _last_pull_status
    _last_pull_status = _git_pull()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
