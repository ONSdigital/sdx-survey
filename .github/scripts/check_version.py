import toml
import re
import subprocess
import sys


def compare_versions(new_version: str, current_version: str) -> int:
    """
    Compare two versions.
    :param new_version: The version from the PR
    :param current_version: The version that is currently in the main branch
    Returns:
      1 if new_version > current_version
     -1 if new_version < current_version
      0 if equal
    """
    pr_parts = list(map(int, new_version.split(".")))
    main_parts = list(map(int, current_version.split(".")))

    if pr_parts > main_parts:
        return 1
    elif pr_parts < main_parts:
        return -1
    else:
        return 0


# --- PR version ---
with open("pyproject.toml", "r") as file:
    pyproject = toml.load(file)
    pr_version = pyproject["project"]["version"]

print(f"PR Version: {pr_version}")

# --- Fetch main branch ---
try:
    subprocess.run(
        ["git", "fetch", "origin", "main"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
except subprocess.CalledProcessError:
    print("⚠️  Could not fetch origin/main. Skipping version comparison.")
    sys.exit(0)

# --- Main branch version (without checkout) ---
try:
    git_show = subprocess.run(
        ["git", "show", "origin/main:pyproject.toml"],
        check=True,
        text=True,
        capture_output=True,
    )
    main_branch_pyproject = toml.loads(git_show.stdout)
    main_version = main_branch_pyproject["project"]["version"]
except subprocess.CalledProcessError:
    print("⚠️  No pyproject.toml found on origin/main. Skipping version comparison.")
    sys.exit(0)

print(f"Main Branch Version: {main_version}")

# --- Validate version format ---
version_regex = r"^\d+\.\d+\.\d+$"
if not re.match(version_regex, pr_version) or not re.match(version_regex, main_version):
    raise ValueError("One of the versions does not match the expected format (major.minor.patch).")

# --- Compare ---
comparison_result = compare_versions(pr_version, main_version)

if comparison_result <= 0:
    raise ValueError(f"PR version ({pr_version}) must be greater than the main branch version ({main_version}).")
else:
    print(f"✅ PR version {pr_version} is greater than the main branch version {main_version}.")
