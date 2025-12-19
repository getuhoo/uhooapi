#!/usr/bin/env python3
"""Script to bump version and create changelog."""

import re
import sys
import subprocess
from pathlib import Path
from datetime import datetime


def bump_version(version_type="patch"):
    """Bump version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    # Find current version
    version_match = re.search(r'version = "([\d.]+)"', content)
    if not version_match:
        print("ERROR: Could not find version in pyproject.toml")
        sys.exit(1)

    current_version = version_match.group(1)
    major, minor, patch = map(int, current_version.split("."))

    # Bump version
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1

    new_version = f"{major}.{minor}.{patch}"

    # Update pyproject.toml
    new_content = re.sub(r'version = "[\d.]+"', f'version = "{new_version}"', content)
    pyproject_path.write_text(new_content)

    # Update __init__.py if it has version
    init_path = Path("src/uhooapi/__init__.py")
    if init_path.exists():
        init_content = init_path.read_text()
        if "__version__" in init_content:
            init_content = re.sub(
                r'__version__ = "[\d.]+"',
                f'__version__ = "{new_version}"',
                init_content,
            )
            init_path.write_text(init_content)

    print(f"Bumped version from {current_version} to {new_version}")
    return new_version


def update_changelog(version, version_type):
    """Update CHANGELOG.md."""
    changelog_path = Path("CHANGELOG.md")

    # Get git log since last tag
    try:
        last_tag = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"], capture_output=True, text=True
        ).stdout.strip()
        log_cmd = ["git", "log", f"{last_tag}..HEAD", "--oneline", "--no-merges"]
    except subprocess.CalledProcessError:
        log_cmd = ["git", "log", "--oneline", "--no-merges", "-n", "20"]

    commits = (
        subprocess.run(log_cmd, capture_output=True, text=True)
        .stdout.strip()
        .split("\n")
    )

    # Create changelog entry
    today = datetime.now().strftime("%Y-%m-%d")
    entry = f"## [{version}] - {today}\n\n"

    if commits:
        entry += "### Changes\n"
        for commit in commits:
            if commit:
                entry += f"- {commit}\n"
    else:
        entry += "### No changes recorded\n"

    entry += "\n"

    # Prepend to changelog
    if changelog_path.exists():
        old_content = changelog_path.read_text()
    else:
        old_content = "# Changelog\n\n"

    # Insert after the header
    lines = old_content.split("\n")
    if lines[0].startswith("# Changelog"):
        new_content = "\n".join(lines[:2]) + "\n\n" + entry + "\n".join(lines[2:])
    else:
        new_content = "# Changelog\n\n" + entry + old_content

    changelog_path.write_text(new_content)
    print("Updated CHANGELOG.md")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ["major", "minor", "patch"]:
        print("Usage: python scripts/bump_version.py [major|minor|patch]")
        sys.exit(1)

    version_type = sys.argv[1]
    new_version = bump_version(version_type)
    update_changelog(new_version, version_type)

    # Commit changes
    subprocess.run(
        ["git", "add", "pyproject.toml", "CHANGELOG.md", "src/uhooapi/__init__.py"]
    )
    subprocess.run(["git", "commit", "-m", f"Bump version to {new_version}"])

    print(f"\n✅ Version bumped to {new_version}")
    print("Run: git push origin main")


if __name__ == "__main__":
    main()
