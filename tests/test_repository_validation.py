"""Validate portable package failures using isolated repository fixtures."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "validate.py"


class RepositoryValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def package(self, name="sample-skill", metadata=None, body="Use this skill for examples.\n"):
        package = self.root / name
        package.mkdir(exist_ok=True)
        metadata = metadata if metadata is not None else f"name: {name}\ndescription: Handle sample tasks.\n"
        (package / "SKILL.md").write_text(f"---\n{metadata}---\n{body}", encoding="utf-8")
        return package

    def check(self, expected=0):
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_multiline_yaml_optional_resources_and_extensions_are_valid(self):
        package = self.package(metadata="""name: sample-skill
description: >-
  Handle sample tasks
  ---
  when a user asks for an example.
license: MIT
compatibility: Requires Python 3.
allowed-tools: Bash(python:*) Read
metadata:
  author: Example
  version: "1.0"
x-client-option:
  mode: example
""", body="""Read [a valid spaced path](<custom folder/guide.md> "Guide").
See [the reference][guide], [Guide][], and [guide].

[guide]: <custom folder/guide.md>

Use [balanced parentheses](custom/guide(v2).md).
![asset](custom/icon.svg)
[fragment](#usage) [remote](https://example.com/missing) [email](mailto:a@example.com)
[network URL](//example.com/missing)
""")
        (package / "custom folder").mkdir()
        (package / "custom folder" / "guide.md").write_text("# Guide\n", encoding="utf-8")
        (package / "custom").mkdir()
        (package / "custom" / "guide(v2).md").write_text("# Guide\n", encoding="utf-8")
        (package / "custom" / "icon.svg").write_text("<svg/>\n", encoding="utf-8")
        self.package("minimal-skill")
        self.package("中文-skill")
        self.assertIn("Validated 3 skill package(s).", self.check().stdout)

    def test_invalid_yaml_and_required_field_types_fail(self):
        cases = (
            ("name: [unfinished\n", "invalid YAML"),
            ("- name\n- description\n", "YAML mapping"),
            ("description: Has no name.\n", "name must"),
            ("name: sample-skill\ndescription: false\n", "description must"),
            ("name: sample-skill\ndescription: '   '\n", "description must"),
            ("name: sample-skill\ndescription: " + "x" * 1025 + "\n", "description must"),
        )
        for metadata, expected in cases:
            with self.subTest(metadata=metadata[:80]):
                self.package(metadata=metadata)
                self.assertIn(expected, self.check(expected=1).stderr)

    def test_name_and_supported_optional_fields_follow_spec(self):
        cases = (
            ("name: other-name\ndescription: Example.\n", "must match package directory"),
            ("name: sample--skill\ndescription: Example.\n", "name must"),
            ("name: Sample\ndescription: Example.\n", "name must"),
            ("name: " + "a" * 65 + "\ndescription: Example.\n", "name must"),
            ("metadata:\n  version: 1.0\n", "metadata must map"),
            ("compatibility: " + "x" * 501 + "\n", "compatibility must"),
            ("allowed-tools: [Read, Bash]\n", "allowed-tools must be a string"),
        )
        for metadata, expected in cases:
            with self.subTest(metadata=metadata[:80]):
                if not metadata.startswith("name:"):
                    metadata = "name: sample-skill\ndescription: Example.\n" + metadata
                self.package(metadata=metadata)
                self.assertIn(expected, self.check(expected=1).stderr)

    def test_broken_links_and_package_escapes_fail_including_reference_images(self):
        self.package(body="""[broken](references/missing.md#section)
![image][asset]

[asset]: assets/missing.png

[escape](../shared.md)
[absolute](/tmp/example.md)
""")
        (self.root / "shared.md").write_text("Present but outside the package.\n", encoding="utf-8")
        errors = self.check(expected=1).stderr
        self.assertIn("references/missing.md#section", errors)
        self.assertIn("assets/missing.png", errors)
        self.assertIn("escapes skill package: ../shared.md", errors)
        self.assertIn("package-relative path: /tmp/example.md", errors)

    def test_fenced_and_inline_examples_do_not_create_false_broken_links(self):
        self.package(body="""```markdown
[example](does-not-exist.md)
```
~~~markdown
[another](../outside.md)
~~~
An inline example: `[example](missing.md)`.
And a two-backtick example: ``[example](missing.md)``.
[unused]: missing.md
""")
        self.check()

    def test_percent_encoded_links_and_symlink_escapes(self):
        package = self.package(body="[resource](resources/with%20space.md?download=1#part)\n")
        (package / "resources").mkdir()
        (package / "resources" / "with space.md").write_text("# Resource\n", encoding="utf-8")
        self.check()
        outside = self.root / "outside.md"
        outside.write_text("Outside.\n", encoding="utf-8")
        try:
            (package / "linked.md").symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Creating symlinks is unavailable on this host")
        self.package(body="[escape through link](linked.md)\n")
        self.assertIn("escapes skill package", self.check(expected=1).stderr)

    def test_commonmark_ignores_indented_code_comments_and_links_inside_autolinks(self):
        self.package(body="""    [indented code](missing.md)

<!-- [comment](missing.md) -->

Visible text <!-- [inline comment](missing.md) --> continues.

<https://example.com/[x](missing.md)>

<a href="missing.md">HTML links are outside this check's scope.</a>
""")
        self.check()

    def test_commonmark_retains_real_links_next_to_comments_and_file_uris(self):
        self.package(body="""<!-- [hidden](hidden.md) -->

[real](missing.md)

[host file](file:///tmp/example.md)
""")
        errors = self.check(expected=1).stderr
        self.assertNotIn("hidden.md", errors)
        self.assertIn("does not exist: missing.md", errors)
        self.assertIn("package-relative path: file:///tmp/example.md", errors)

    def test_rooted_url_paths_fail_consistently_on_every_platform(self):
        for target in ("/tmp/example.md", r"\tmp\example.md", r"\\server\share\example.md",
                       "%2Ftmp/example.md", "%5Ctmp%5Cexample.md",
                       "%5C%5Cserver%5Cshare%5Cexample.md", "C:%5Ctmp%5Cexample.md"):
            with self.subTest(target=target):
                self.package(body=f"[host path]({target})\n")
                self.assertIn("package-relative path", self.check(expected=1).stderr)

    def test_missing_or_renamed_packages_cannot_silently_disable_checks(self):
        self.assertIn("No top-level skill packages found", self.check(expected=1).stderr)
        package = self.package()
        (package / "SKILL.md").rename(package / "skill.txt")
        self.assertIn("No top-level skill packages found", self.check(expected=1).stderr)

    def test_missing_frontmatter_is_rejected(self):
        package = self.package()
        for content in ("# No metadata\n", "---\nname: sample-skill\n"):
            with self.subTest(content=content):
                (package / "SKILL.md").write_text(content, encoding="utf-8")
                self.assertIn("missing YAML frontmatter", self.check(expected=1).stderr)


if __name__ == "__main__":
    unittest.main()
