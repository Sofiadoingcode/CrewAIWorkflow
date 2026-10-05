from crewai.tools import tool

from .filesystem import write_file


def create_write_tool(repo_path: str):

    @tool("write_repository_file")
    def write_repository_file(relative_path: str, content: str) -> str:
        """Create or overwrite a file in the target repository with the full file content."""

        return f"Wrote {write_file(repo_path, relative_path, content)}"

    return write_repository_file
