from pathlib import Path


def read_file(repo_path: str, relative_path: str) -> str:
    path = Path(repo_path) / relative_path

    return path.read_text(encoding="utf-8")


def write_file(
    repo_path: str,
    relative_path: str,
    content: str,
) -> str:

    path = Path(repo_path) / relative_path

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        content,
        encoding="utf-8",
    )

    return str(path)


def list_files(repo_path: str) -> list[str]:

    root = Path(repo_path)

    return [
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
    ]

def read_repository(
    repo_path: str,
    max_file_chars: int = 4000,
) -> str:

    sections = []

    for relative_path in sorted(list_files(repo_path)):

        if "__pycache__" in relative_path or relative_path.startswith("."):
            continue

        try:
            content = read_file(repo_path, relative_path)
        except UnicodeDecodeError:
            continue

        sections.append(
            f"--- {relative_path} ---\n"
            f"{content[:max_file_chars]}"
        )

    return "\n\n".join(sections) or "(empty repository)"
