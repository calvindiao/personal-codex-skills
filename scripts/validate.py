#!/usr/bin/env python3
"""Check portable skill metadata and local Markdown links; never execute skills.

The metadata rules follow https://agentskills.io/specification. CommonMark
tokens identify links; this check does not evaluate skill quality.
"""

import argparse
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

try:
    import yaml
    from markdown_it import MarkdownIt
except ImportError:
    raise SystemExit("Repository validation requires development dependencies. Install requirements-dev.txt.")


def markdown_links(body):
    """Yield (target, containing block's first line) from CommonMark tokens.

    Code, HTML, and unused reference definitions do not produce link tokens.
    The parser resolves reference links, entities, and Markdown escapes. It
    supplies block-level line maps, not exact positions for individual links.
    """
    parser = MarkdownIt("commonmark")
    # Inspect file: targets too, rather than applying a renderer's URL filter.
    # Parsing never renders, follows, or executes any target.
    parser.validateLink = lambda target: True
    for block in parser.parse(body):
        if block.type != "inline":
            continue
        for token in block.children or []:
            attribute = {"link_open": "href", "image": "src"}.get(token.type)
            if attribute:
                target = token.attrGet(attribute)
                if target is not None:
                    yield target, block.map[0] + 1


def metadata_errors(data, directory):
    if not isinstance(data, dict):
        return ["frontmatter must be a YAML mapping"]
    errors = []
    name = data.get("name")
    # Match the official skills-ref validator's support for international names.
    if isinstance(name, str):
        name = unicodedata.normalize("NFKC", name.strip())
    if (not isinstance(name, str) or not 1 <= len(name) <= 64 or name != name.lower()
            or name.startswith("-") or name.endswith("-") or "--" in name
            or not all(char.isalnum() or char == "-" for char in name)):
        errors.append("name must contain 1-64 lowercase letters/digits and single internal hyphens")
    elif name != unicodedata.normalize("NFKC", directory):
        errors.append(f"name {name!r} must match package directory {directory!r}")
    description = data.get("description")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        errors.append("description must be a non-empty string of at most 1024 characters")
    for field in ("license", "allowed-tools"):
        if field in data and not isinstance(data[field], str):
            errors.append(f"{field} must be a string when present")
    if "compatibility" in data:
        value = data["compatibility"]
        if not isinstance(value, str) or not value.strip() or len(value) > 500:
            errors.append("compatibility must be a non-empty string of at most 500 characters")
    if "metadata" in data:
        value = data["metadata"]
        if not isinstance(value, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in value.items()):
            errors.append("metadata must map string keys to string values")
    return errors


def local_link_error(target, package):
    if re.match(r"^[A-Za-z]:[/\\]", unquote(target)):
        return f"local link must use a package-relative path: {target}"
    try:
        url = urlsplit(target)
    except ValueError:
        return f"invalid link target: {target}"
    if url.scheme.lower() == "file":
        return f"local link must use a package-relative path: {target}"
    if url.scheme or url.netloc or not url.path:
        return None  # Remote URL, fragment-only link, or same-document query.
    decoded_path = unquote(url.path)
    # URL paths are independent of the OS running validation. On Windows,
    # '/tmp/file' has a root but no drive, so Path.is_absolute() alone is false.
    if decoded_path.startswith(("/", "\\")):
        return f"local link must use a package-relative path: {target}"
    relative = Path(decoded_path)
    try:
        resolved = (package / relative).resolve()
        resolved.relative_to(package.resolve())
    except ValueError:
        return f"local link escapes skill package: {target}"
    except (OSError, RuntimeError) as error:
        return f"cannot resolve local link {target!r}: {error}"
    if not resolved.exists():
        return f"local link target does not exist: {target}"
    return None


def validate(root):
    """Discover immediate child packages, returning their count and diagnostics."""
    skills = sorted(root.glob("*/SKILL.md"))
    if not skills:
        return 0, ["No top-level skill packages found; expected <skill-name>/SKILL.md."]
    errors = []
    for skill in skills:
        display = skill.relative_to(root).as_posix()
        try:
            text = skill.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            errors.append(f"{display}: cannot read UTF-8: {error}")
            continue
        lines = text.splitlines(keepends=True)
        if not lines or lines[0].rstrip() != "---":
            errors.append(f"{display}:1: missing YAML frontmatter opening ---")
            continue
        end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
        if end is None:
            errors.append(f"{display}:1: missing YAML frontmatter closing ---")
            continue
        try:
            data = yaml.safe_load("".join(lines[1:end]))
        except yaml.YAMLError as error:
            detail = str(error).splitlines()[0]
            errors.append(f"{display}: invalid YAML: {detail}")
            continue
        errors.extend(f"{display}: {error}" for error in metadata_errors(data, skill.parent.name))
        for target, line in markdown_links("".join(lines[end + 1:])):
            error = local_link_error(target, skill.parent)
            if error:
                errors.append(f"{display}:{end + 1 + line}: {error}")
    return len(skills), errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="repository to check (default: this script's repository)")
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error(f"repository directory does not exist: {args.root}")
    count, errors = validate(args.root.resolve())
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {count} skill package(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
