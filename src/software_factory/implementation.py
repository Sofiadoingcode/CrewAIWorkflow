from concurrent.futures import ThreadPoolExecutor, as_completed

from .agents.coding_worker import run_coding_worker


def run_parallel_workers(
    state,
    tickets,
):

    workers = [
        {
            "name": "Backend Worker",
            "role": "Backend Coding Worker",
            "goal": (
                "Implement backend, domain, persistence, "
                "and data-layer tickets."
            ),
        },
        {
            "name": "API Worker",
            "role": "API and Integration Coding Worker",
            "goal": (
                "Implement API, integration, and API-level "
                "testing tickets."
            ),
        },
    ]

    results = []

    with ThreadPoolExecutor(
        max_workers=len(workers)
    ) as executor:

        futures = []

        for worker in workers:

            future = executor.submit(
                run_coding_worker,
                worker["name"],
                worker["role"],
                worker["goal"],
                state.repo_path,
                state.feature_request,
                state.architecture,
                tickets,
            )

            futures.append(future)

        for future in as_completed(futures):
            results.append(
                future.result()
            )

    return results