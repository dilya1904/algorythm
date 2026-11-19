"""Standalone verification tests for BFS vs DFS FastAPI server & algorithm engine."""

from main import (
    GenerateMazeRequest,
    SolveMazeRequest,
    health_check,
    maze_generate,
    maze_presets,
    read_root,
    solve_maze,
)


def test_health_and_root():
    root = read_root()
    assert root["status"] == "online"

    health = health_check()
    assert health["status"] == "healthy"
    assert "gemini_api_key_configured" in health


def test_presets_and_generate():
    presets_resp = maze_presets()
    assert presets_resp["status"] == "ok"
    assert len(presets_resp["presets"]) >= 4

    gen_resp = maze_generate(GenerateMazeRequest(rows=11, cols=11, seed=42))
    maze = gen_resp["maze"]
    assert maze["rows"] == 11 and maze["cols"] == 11
    assert maze["grid"][maze["start"][0]][maze["start"][1]] == 0
    assert maze["grid"][maze["goal"][0]][maze["goal"][1]] == 0


def test_solve_bfs_vs_dfs_snapshots_and_histograms():
    for preset_id in ("classic_branch", "open_corridor", "dead_end_trap", "spiral_labyrinth"):
        resp = solve_maze(SolveMazeRequest(preset_id=preset_id))
        assert resp["status"] == "ok"
        data = resp["data"]
        bfs = data["bfs"]
        dfs = data["dfs"]

        assert bfs["summary"]["found"] is True
        assert dfs["summary"]["found"] is True
        assert bfs["summary"]["path_length"] <= dfs["summary"]["path_length"]

        for algo in (bfs, dfs):
            assert len(algo["steps"]) >= 2
            for snap in algo["steps"]:
                assert "elapsed_ms" in snap
                tc = snap["time_complexity"]
                assert tc["notation"] == "O(V + E)"
                assert 0.0 <= tc["progress_pct"] <= 100.0
                bins = snap["histogram"]["depth_bins"]
                assert isinstance(bins, list) and len(bins) >= 1
                assert "metrics" in snap["histogram"]

        print(
            f"[{preset_id}] BFS(path={bfs['summary']['path_length']}, visited={bfs['summary']['visited_count']}, maxQ={bfs['summary']['max_frontier_size']}) "
            f"vs DFS(path={dfs['summary']['path_length']}, visited={dfs['summary']['visited_count']}, maxS={dfs['summary']['max_frontier_size']}, backtracks={dfs['summary']['backtrack_count']})"
        )


def test_unsolvable_maze():
    grid = [
        [1, 1, 1, 1, 1],
        [1, 0, 1, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    resp = solve_maze(SolveMazeRequest(grid=grid, start=[1, 1], goal=[1, 3]))
    data = resp["data"]
    assert data["bfs"]["summary"]["found"] is False
    assert data["dfs"]["summary"]["found"] is False
    assert data["bfs"]["steps"][-1]["phase"] == "NO_PATH"
    assert data["dfs"]["steps"][-1]["phase"] == "NO_PATH"


if __name__ == "__main__":
    test_health_and_root()
    test_presets_and_generate()
    test_solve_bfs_vs_dfs_snapshots_and_histograms()
    test_unsolvable_maze()
    print("ALL SERVER TESTS PASSED")
