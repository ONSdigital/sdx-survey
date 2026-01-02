from tomlkit import parse, dumps


def bump_patch(version: str) -> str:
    major, minor, patch = map(int, version.split("."))
    patch += 1
    return f"{major}.{minor}.{patch}"


# --- read TOML ---
with open("pyproject.toml", "r") as f:
    pyproject = parse(f.read())

# --- bump version ---
current_version = pyproject["project"]["version"]
new_version = bump_patch(current_version)
pyproject["project"]["version"] = new_version

# --- write back ---
with open("pyproject.toml", "w") as f:
    f.write(dumps(pyproject))

print(f"Version bumped: {current_version} → {new_version}")
