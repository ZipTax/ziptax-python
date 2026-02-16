#!/usr/bin/env python3
"""Version bump utility for ziptax-python SDK.

This script helps maintain consistent versioning across the project by updating
version numbers in all required files.

Usage:
    python scripts/bump_version.py patch    # 0.1.4-beta -> 0.1.5-beta
    python scripts/bump_version.py minor    # 0.1.4-beta -> 0.2.0-beta
    python scripts/bump_version.py major    # 0.1.4-beta -> 1.0.0-beta
    python scripts/bump_version.py 0.2.0    # Set specific version
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Tuple


def parse_version(version_str: str) -> Tuple[int, int, int, str]:
    """Parse version string into components.

    Args:
        version_str: Version string like "0.1.4-beta"

    Returns:
        Tuple of (major, minor, patch, suffix)

    Raises:
        ValueError: If version format is invalid
    """
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$", version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")

    major, minor, patch, suffix = match.groups()
    return int(major), int(minor), int(patch), suffix or ""


def format_version(major: int, minor: int, patch: int, suffix: str = "") -> str:
    """Format version components into string.

    Args:
        major: Major version number
        minor: Minor version number
        patch: Patch version number
        suffix: Optional suffix like "beta", "alpha", "rc1"

    Returns:
        Formatted version string
    """
    version = f"{major}.{minor}.{patch}"
    if suffix:
        version += f"-{suffix}"
    return version


def get_current_version() -> str:
    """Get current version from pyproject.toml.

    Returns:
        Current version string

    Raises:
        FileNotFoundError: If pyproject.toml not found
        ValueError: If version not found in file
    """
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")

    content = pyproject_path.read_text()
    match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)

    if not match:
        raise ValueError("Version not found in pyproject.toml")

    return match.group(1)


def bump_version(current: str, bump_type: str) -> str:
    """Bump version according to type.

    Args:
        current: Current version string
        bump_type: One of "major", "minor", "patch", or explicit version

    Returns:
        New version string

    Raises:
        ValueError: If bump_type is invalid
    """
    # If bump_type looks like a version, use it directly
    if re.match(r"^\d+\.\d+\.\d+", bump_type):
        # Validate the version format
        parse_version(bump_type)
        return bump_type

    major, minor, patch, suffix = parse_version(current)

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(
            f"Invalid bump type: {bump_type}. "
            f"Use 'major', 'minor', 'patch', or explicit version."
        )

    return format_version(major, minor, patch, suffix)


def update_pyproject_toml(new_version: str) -> None:
    """Update version in pyproject.toml.

    Args:
        new_version: New version string
    """
    path = Path("pyproject.toml")
    content = path.read_text()

    # Replace version line
    new_content = re.sub(
        r'^version\s*=\s*["\'][^"\']+["\']',
        f'version = "{new_version}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )

    path.write_text(new_content)
    print(f"✅ Updated pyproject.toml")


def update_init_py(new_version: str) -> None:
    """Update __version__ in src/ziptax/__init__.py.

    Args:
        new_version: New version string
    """
    path = Path("src/ziptax/__init__.py")
    content = path.read_text()

    # Replace __version__ line
    new_content = re.sub(
        r'^__version__\s*=\s*["\'][^"\']+["\']',
        f'__version__ = "{new_version}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )

    path.write_text(new_content)
    print(f"✅ Updated src/ziptax/__init__.py")


def update_claude_md(new_version: str) -> None:
    """Update version reference in CLAUDE.md.

    Args:
        new_version: New version string
    """
    path = Path("CLAUDE.md")
    if not path.exists():
        print("⚠️  CLAUDE.md not found, skipping")
        return

    content = path.read_text()

    # Replace SDK Version line
    new_content = re.sub(
        r'\*\*SDK Version\*\*:\s*[^\n]+',
        f'**SDK Version**: {new_version}',
        content,
    )

    path.write_text(new_content)
    print(f"✅ Updated CLAUDE.md")


def verify_consistency() -> bool:
    """Verify version consistency across all files.

    Returns:
        True if all versions match, False otherwise
    """
    # Get version from pyproject.toml
    pyproject_path = Path("pyproject.toml")
    pyproject_content = pyproject_path.read_text()
    pyproject_match = re.search(
        r'^version\s*=\s*["\']([^"\']+)["\']', pyproject_content, re.MULTILINE
    )
    pyproject_version = pyproject_match.group(1) if pyproject_match else None

    # Get version from __init__.py
    init_path = Path("src/ziptax/__init__.py")
    init_content = init_path.read_text()
    init_match = re.search(
        r'^__version__\s*=\s*["\']([^"\']+)["\']', init_content, re.MULTILINE
    )
    init_version = init_match.group(1) if init_match else None

    # Get version from CLAUDE.md
    claude_path = Path("CLAUDE.md")
    claude_version = None
    if claude_path.exists():
        claude_content = claude_path.read_text()
        claude_match = re.search(r'\*\*SDK Version\*\*:\s*([^\n]+)', claude_content)
        claude_version = claude_match.group(1).strip() if claude_match else None

    print("\n📋 Version Check:")
    print(f"   pyproject.toml: {pyproject_version}")
    print(f"   __init__.py:    {init_version}")
    print(f"   CLAUDE.md:      {claude_version or 'N/A'}")

    all_match = (
        pyproject_version == init_version
        and (not claude_version or pyproject_version == claude_version)
    )

    if all_match:
        print("✅ All versions match!")
    else:
        print("❌ Version mismatch detected!")

    return all_match


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Bump version numbers across the project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Bump patch version (0.1.4 -> 0.1.5)
  python scripts/bump_version.py patch

  # Bump minor version (0.1.4 -> 0.2.0)
  python scripts/bump_version.py minor

  # Bump major version (0.1.4 -> 1.0.0)
  python scripts/bump_version.py major

  # Set specific version
  python scripts/bump_version.py 0.2.0-beta

  # Just check version consistency
  python scripts/bump_version.py --check
        """,
    )
    parser.add_argument(
        "bump_type",
        nargs="?",
        help="Type of version bump (major, minor, patch) or explicit version (e.g. 0.2.0-beta)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check version consistency without bumping",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )

    args = parser.parse_args()

    # Check mode
    if args.check:
        return 0 if verify_consistency() else 1

    # Require bump_type if not in check mode
    if not args.bump_type:
        parser.error("bump_type is required when not using --check")

    try:
        # Get current and new versions
        current_version = get_current_version()
        new_version = bump_version(current_version, args.bump_type)

        print(f"\n🔄 Version Bump: {current_version} → {new_version}\n")

        if args.dry_run:
            print("🔍 Dry run mode - no files will be modified\n")
            print("Would update:")
            print("  - pyproject.toml")
            print("  - src/ziptax/__init__.py")
            print("  - CLAUDE.md")
            return 0

        # Update all files
        update_pyproject_toml(new_version)
        update_init_py(new_version)
        update_claude_md(new_version)

        print()

        # Verify consistency
        if verify_consistency():
            print("\n✨ Version bump complete!")
            print("\n📝 Next steps:")
            print("   1. Update CHANGELOG.md with your changes")
            print("   2. Commit changes: git add -A && git commit -m 'Bump version to {}'".format(new_version))
            print("   3. Create PR with version bump")
            return 0
        else:
            print("\n⚠️  Version bump completed but consistency check failed!")
            return 1

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
