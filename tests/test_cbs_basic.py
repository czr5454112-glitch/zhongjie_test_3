from standard_cbs import Agent, CBS, GridMap, ProblemInstance


def test_two_agents_swap_positions():
    grid = GridMap(width=3, height=2, obstacles=set())
    agents = [
        Agent(name="a1", start=(0, 0), goal=(2, 1)),
        Agent(name="a2", start=(2, 1), goal=(0, 0)),
    ]

    solver = CBS(grid)
    solution = solver.solve(ProblemInstance(agents=agents))

    assert solution.paths["a1"][0] == (0, 0)
    assert solution.paths["a1"][-1] == (2, 1)
    assert solution.paths["a2"][0] == (2, 1)
    assert solution.paths["a2"][-1] == (0, 0)

    makespan = solution.makespan()
    for t in range(makespan + 1):
        pos_a1 = solution.paths["a1"][t] if t < len(solution.paths["a1"]) else solution.paths["a1"][-1]
        pos_a2 = solution.paths["a2"][t] if t < len(solution.paths["a2"]) else solution.paths["a2"][-1]
        assert pos_a1 != pos_a2





