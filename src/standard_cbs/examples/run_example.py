from __future__ import annotations

from standard_cbs import Agent, CBS, GridMap, ProblemInstance


def main() -> None:
    obstacles = {(2, 1), (2, 2), (2, 3)}
    grid = GridMap(width=5, height=5, obstacles=obstacles)

    agents = [
        Agent(name="agent_1", start=(0, 0), goal=(4, 0)),
        Agent(name="agent_2", start=(0, 1), goal=(4, 1)),
    ]

    problem = ProblemInstance(agents=agents)
    solver = CBS(grid)

    solution = solver.solve(problem)

    print("总成本:", solution.cost)
    for agent, path in solution.paths.items():
        path_str = " -> ".join(f"({x},{y})" for x, y in path)
        print(f"{agent}: {path_str}")


if __name__ == "__main__":
    main()





