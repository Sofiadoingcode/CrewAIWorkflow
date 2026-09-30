from .flow import SoftwareFactoryFlow
from dotenv import load_dotenv

load_dotenv()

def main():

    repo_path = input(
        "Path to target repository: "
    ).strip()

    feature_request = input(
        "Feature request: "
    ).strip()

    flow = SoftwareFactoryFlow()

    result = flow.kickoff(
        inputs={
            "repo_path": repo_path,
            "feature_request": feature_request,
        }
    )

    print("\n")
    print("=" * 80)
    print("SOFTWARE FACTORY COMPLETE")
    print("=" * 80)

    print(result)


if __name__ == "__main__":
    main()