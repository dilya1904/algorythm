"""Standalone verification tests for DijkstraLab Navigation Graph FastAPI server."""

import sys
from pathlib import Path

_CURRENT_DIR = Path(__file__).resolve().parent
if str(_CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(_CURRENT_DIR))

from main import (
    ALLOWED_ORIGINS,
    GenerateGraphRequest,
    SolveDijkstraRequest,
    graph_generate,
    graph_presets,
    health_check,
    read_root,
    solve_dijkstra,
)


def test_health_and_cors():
    assert read_root()["status"] == "online"
    h = health_check()
    assert h["status"] == "healthy"
    assert h["connected"] is True
    assert "gemini_api_key_configured" in h
    assert "https://script.google.com" in ALLOWED_ORIGINS
    assert "https://script.googleusercontent.com" in ALLOWED_ORIGINS


def test_presets_and_solve():
    presets = graph_presets()["presets"]
    assert len(presets) >= 3

    for p in presets:
        res = solve_dijkstra(SolveDijkstraRequest(preset_id=p["id"]))
        assert res["status"] == "ok"
        data = res["data"]
        assert data["summary"]["found"] is True
        assert data["summary"]["shortest_cost"] > 0
        assert len(data["steps"]) >= 2
        print(
            f"[{p['id']}] Path={'->'.join(data['summary']['shortest_path'])} "
            f"cost={data['summary']['shortest_cost']} ops={data['summary']['operations']}"
        )


def test_campus_nav_exact_shortest_path():
    # A->C(2)->D(3)->E(3)->G(5) = 13 vs A->C(2)->D(3)->F(6)->G(2) = 13 vs A->C(2)->F(9)->G(2) = 13
    res = solve_dijkstra(SolveDijkstraRequest(preset_id="campus_nav"))
    assert res["data"]["summary"]["shortest_cost"] == 13


def test_random_graph_and_solve():
    gen = graph_generate(GenerateGraphRequest(node_count=7, seed=7))["graph"]
    res = solve_dijkstra(
        SolveDijkstraRequest(
            graph_name=gen["name"],
            nodes=gen["nodes"],
            edges=gen["edges"],
            start=gen["start"],
            target=gen["target"],
        )
    )
    assert res["data"]["summary"]["found"] is True


if __name__ == "__main__":
    test_health_and_cors()
    test_presets_and_solve()
    test_campus_nav_exact_shortest_path()
    test_random_graph_and_solve()
    print("ALL NAVIGATION GRAPH TESTS PASSED")
