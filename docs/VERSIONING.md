# Versioning Guide

This document describes the versioning strategy and processes for the ZipTax Python SDK.

## Table of Contents

- [Versioning Strategy](#versioning-strategy)
- [Semantic Versioning](#semantic-versioning)
- [Version Bump Process](#version-bump-process)
- [Automated Checks](#automated-checks)
- [Release Process](#release-process)

---

## Versioning Strategy

The ZipTax Python SDK follows [Semantic Versioning 2.0.0](https://semver.org/) with pre-release labels for beta versions.

### Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE]

Examples:
  1.0.0         # Stable release
  0.1.4-beta    # Beta pre-release
  2.1.0-rc1     # Release candidate
```

### Version Components

- **MAJOR**: Incremented for breaking changes
- **MINOR**: Incremented for new features (backward compatible)
- **PATCH**: Incremented for bug fixes (backward compatible)
- **PRERELEASE**: Optional label like `beta`, `alpha`, `rc1`

---

## Semantic Versioning

### When to Bump Each Component

#### Major Version (X.0.0)

Bump the major version when making **breaking changes**:

- Removing public APIs or functions
- Changing function signatures in non-backward-compatible ways
- Changing response model structures
- Removing or renaming model fields
- Changing default behavior that breaks existing code

**Example**: Removing `GetSalesTaxByAddress()` or changing its required parameters.

#### Minor Version (0.X.0)

Bump the minor version when adding **new features**:

- Adding new API endpoints
- Adding new optional parameters
- Adding new models or fields (backward compatible)
- Adding new exception types
- Enhancing existing features without breaking changes

**Example**: Adding TaxCloud order management features (0.1.3 → 0.2.0).

#### Patch Version (0.0.X)

Bump the patch version for **bug fixes and minor improvements**:

- Fixing bugs in existing functionality
- Improving error messages
- Documentation updates
- Performance improvements
- Dependency updates (non-breaking)

**Example**: Fixing a validation bug (0.1.4 → 0.1.5).

### Pre-release Labels

Use pre-release labels for unstable versions:

- **alpha**: Early testing, features incomplete or unstable
- **beta**: Feature complete, but may have bugs
- **rc1, rc2, ...**: Release candidates, nearly ready for production

**Examples**:
- `0.2.0-alpha` → `0.2.0-beta` → `0.2.0-rc1` → `0.2.0`

---

## Version Bump Process

### Using the Version Bump Script

We provide a helper script to maintain version consistency across all files.

#### Check Current Version

```bash
python scripts/bump_version.py --check
```

Output:
```
📋 Version Check:
   pyproject.toml: 0.1.4-beta
   __init__.py:    0.1.4-beta
   CLAUDE.md:      0.1.4-beta
✅ All versions match!
```

#### Bump Patch Version

For bug fixes and minor improvements:

```bash
python scripts/bump_version.py patch
```

Output:
```
🔄 Version Bump: 0.1.4-beta → 0.1.5-beta

✅ Updated pyproject.toml
✅ Updated src/ziptax/__init__.py
✅ Updated CLAUDE.md

📋 Version Check:
   pyproject.toml: 0.1.5-beta
   __init__.py:    0.1.5-beta
   CLAUDE.md:      0.1.5-beta
✅ All versions match!

✨ Version bump complete!

📝 Next steps:
   1. Update CHANGELOG.md with your changes
   2. Commit changes: git add -A && git commit -m 'Bump version to 0.1.5-beta'
   3. Create PR with version bump
```

#### Bump Minor Version

For new features:

```bash
python scripts/bump_version.py minor
```

This will bump `0.1.4-beta` → `0.2.0-beta`

#### Bump Major Version

For breaking changes:

```bash
python scripts/bump_version.py major
```

This will bump `0.1.4-beta` → `1.0.0-beta`

#### Set Specific Version

```bash
python scripts/bump_version.py 1.0.0
python scripts/bump_version.py 0.2.0-beta
```

#### Dry Run

Preview changes without modifying files:

```bash
python scripts/bump_version.py patch --dry-run
```

### Manual Version Update

If you prefer to update versions manually, ensure consistency across these files:

1. **pyproject.toml** (line 7):
   ```toml
   version = "0.1.5-beta"
   ```

2. **src/ziptax/__init__.py** (line 47):
   ```python
   __version__ = "0.1.5-beta"
   ```

3. **CLAUDE.md** (near end):
   ```markdown
   **SDK Version**: 0.1.5-beta
   ```

4. **CHANGELOG.md**:
   Update the `[Unreleased]` section with your changes.

---

## Automated Checks

### GitHub Actions Workflow

Every pull request triggers the **Version Bump Check** workflow (`.github/workflows/version-check.yml`) which:

1. ✅ **Verifies version was bumped** compared to base branch
2. ✅ **Checks version consistency** across all files
3. ✅ **Validates semantic versioning** format (PEP 440)
4. ⚠️ **Warns if CHANGELOG.md** wasn't updated
5. 💬 **Posts a comment** on the PR with version info

### What the Workflow Checks

```
┌─────────────────────────────────────────┐
│ Pull Request #123                       │
├─────────────────────────────────────────┤
│ Base: main (0.1.4-beta)                │
│ PR: feature-branch (0.1.5-beta)        │
└─────────────────────────────────────────┘
                  │
                  ▼
        ┌──────────────────┐
        │ Version Checks   │
        └──────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   ┌─────────┐       ┌──────────┐
   │ Bumped? │       │Consistent?│
   │ 0.1.4   │       │pyproject  │
   │   →     │       │__init__   │
   │ 0.1.5   │       │CLAUDE.md  │
   └─────────┘       └──────────┘
        │                   │
        └─────────┬─────────┘
                  ▼
          ┌──────────────┐
          │ Valid Format?│
          │ PEP 440      │
          └──────────────┘
                  │
                  ▼
          ┌──────────────┐
          │CHANGELOG.md? │
          │  (warning)   │
          └──────────────┘
                  │
                  ▼
          ┌──────────────┐
          │ PR Comment   │
          │  with info   │
          └──────────────┘
```

### Example PR Comment

The workflow posts this comment on your PR:

```markdown
## Version Bump Check

| Item | Status |
|------|--------|
| Base version | `0.1.4-beta` |
| PR version | `0.1.5-beta` |
| Version bumped | ✅ Yes |
| Version consistent | ✅ Yes |
| CHANGELOG updated | ⚠️ No |

> ⚠️ **Reminder**: Please update CHANGELOG.md with your changes.

---
Version bump: `0.1.4-beta` → `0.1.5-beta`
```

### What Happens on Failure

If the version check fails, the workflow will:

- ❌ Fail the PR check
- 💬 Comment explaining the issue
- 🚫 Block merging (if branch protection is enabled)

**Common failure scenarios**:

1. **Version not bumped**:
   ```
   ❌ ERROR: Version not bumped!
   Current version (0.1.4-beta) must be greater than base version (0.1.4-beta)
   ```

2. **Version mismatch**:
   ```
   ❌ ERROR: Version mismatch!
   pyproject.toml has 0.1.5-beta
   __init__.py has 0.1.4-beta
   Both files must have the same version.
   ```

3. **Invalid format**:
   ```
   ❌ ERROR: Invalid version format: 0.1.beta
   Error: Invalid version: '0.1.beta'
   ```

---

## Release Process

### Pre-release (Beta)

1. **Create feature branch**:
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement changes** and write tests

3. **Bump version**:
   ```bash
   python scripts/bump_version.py minor  # or patch/major
   ```

4. **Update CHANGELOG.md**:
   ```markdown
   ## [Unreleased]

   ### Added
   - New feature description
   ```

5. **Commit and push**:
   ```bash
   git add -A
   git commit -m "feat: Add new feature

   Bump version to 0.2.0-beta"
   git push origin feature/new-feature
   ```

6. **Create Pull Request**
   - Automated checks will validate version bump
   - Review and merge when approved

7. **Tag the release** (after merge):
   ```bash
   git checkout main
   git pull origin main
   git tag v0.2.0-beta
   git push origin v0.2.0-beta
   ```

### Stable Release

1. **Remove pre-release label**:
   ```bash
   python scripts/bump_version.py 1.0.0
   ```

2. **Update CHANGELOG.md**:
   ```markdown
   ## [1.0.0] - 2024-03-01

   ### Added
   - Feature A
   - Feature B

   ### Changed
   - Improvement X
   ```

3. **Create release PR**:
   ```bash
   git checkout -b release/v1.0.0
   git add -A
   git commit -m "chore: Release v1.0.0"
   git push origin release/v1.0.0
   ```

4. **Merge and tag**:
   ```bash
   git checkout main
   git pull origin main
   git tag v1.0.0
   git push origin v1.0.0
   ```

5. **Publish to PyPI**:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

---

## Best Practices

### ✅ DO

- **Always bump version** for every PR that changes code
- **Use the helper script** to maintain consistency
- **Update CHANGELOG.md** with clear descriptions
- **Follow semantic versioning** rules strictly
- **Test thoroughly** before releasing
- **Tag releases** in git with `vX.Y.Z` format

### ❌ DON'T

- Don't merge PRs without version bumps
- Don't update versions manually without checking consistency
- Don't skip CHANGELOG updates
- Don't use arbitrary version numbers
- Don't make breaking changes in patch versions
- Don't release without testing

---

## FAQ

### Q: What if I forget to bump the version?

**A**: The GitHub Actions workflow will fail and block the merge. Simply run the bump script and push the changes.

### Q: Can I skip the version bump for documentation changes?

**A**: No. All PRs require version bumps to maintain a clear history. Use patch bumps for documentation-only changes.

### Q: How do I handle multiple PRs with version conflicts?

**A**:
1. Rebase your branch on latest main
2. Run `python scripts/bump_version.py --check` to see current version
3. Bump to the next version
4. Commit and push

### Q: When should I remove the `-beta` label?

**A**: Remove pre-release labels when:
- All planned features are complete
- Test coverage is ≥80%
- No critical bugs exist
- Documentation is complete
- The release is stable enough for production use

### Q: What if the automated check fails incorrectly?

**A**: This is rare, but if it happens:
1. Check that all three files have the same version
2. Verify the version format is valid (X.Y.Z or X.Y.Z-label)
3. Ensure the PR version is greater than the base branch version
4. If still failing, check the workflow logs for details

---

## Additional Resources

- [Semantic Versioning 2.0.0](https://semver.org/)
- [PEP 440 - Version Identification](https://peps.python.org/pep-0440/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Git Tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging)

---

**Questions?** Open an issue or contact the maintainers.
