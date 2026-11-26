"""
Dijkstra Shortest-Path Navigation Graph Engine
Generates step-by-step relaxation snapshots, priority queue previews,
and O((V + E) log V) telemetry metadata for DijkstraLab UI.
"""

import heapq
import math
import random
import time
from typing import Any, Dict, List, Optional, Set, Tuple


PRESET_GRAPHS: Dict[str, Dict[str, Any]] = {
    "campus_nav": {
        "id": "campus_nav",
        "name": "캠퍼스 도로망 네비게이션 (A 공학관 → G 기숙사)",
        "description": "7개 거점과 11개 가중치 도로로 구성된 기본 다익스트라 학습 맵",
        "start": "A",
        "target": "G",
        "nodes": [
            {"id": "A", "label": "공학관", "navX": 90, "navY": 150, "graphX": 60, "graphY": 140},
            {"id": "B", "label": "중앙도서관", "navX": 280, "navY": 65, "graphX": 185, "graphY": 55},
            {"id": "C", "label": "학생회관", "navX": 290, "navY": 235, "graphX": 185, "graphY": 225},
            {"id": "D", "label": "자연과학관", "navX": 485, "navY": 150, "graphX": 300, "graphY": 140},
            {"id": "E", "label": "AI연구센터", "navX": 675, "navY": 65, "graphX": 410, "graphY": 55},
            {"id": "F", "label": "정문", "navX": 685, "navY": 235, "graphX": 410, "graphY": 225},
            {"id": "G", "label": "기숙사", "navX": 870, "navY": 150, "graphX": 485, "graphY": 140},
        ],
        "edges": [
            {"u": "A", "v": "B", "w": 4},
            {"u": "A", "v": "C", "w": 2},
            {"u": "B", "v": "C", "w": 3},
            {"u": "B", "v": "D", "w": 5},
            {"u": "C", "v": "D", "w": 3},
            {"u": "C", "v": "F", "w": 9},
            {"u": "D", "v": "E", "w": 3},
            {"u": "D", "v": "F", "w": 6},
            {"u": "E", "v": "B", "w": 4},
            {"u": "E", "v": "G", "w": 5},
            {"u": "F", "v": "G", "w": 2},
        ],
    },
    "city_express": {
        "id": "city_express",
        "name": "도심 고속도로망 (A 서울역 → H 공항터미널)",
        "description": "우회 고속도로와 시내 단축로가 공존해 거리 완화(Relaxation)가 빈번하게 발생하는 8노드 도로망",
        "start": "A",
        "target": "H",
        "nodes": [
            {"id": "A", "label": "서울역", "navX": 80, "navY": 150, "graphX": 55, "graphY": 140},
            {"id": "B", "label": "마포IC", "navX": 245, "navY": 60, "graphX": 155, "graphY": 55},
            {"id": "C", "label": "여의도", "navX": 245, "navY": 240, "graphX": 155, "graphY": 225},
            {"id": "D", "label": "합정분기", "navX": 455, "navY": 115, "graphX": 270, "graphY": 100},
            {"id": "E", "label": "영등포", "navX": 455, "navY": 225, "graphX": 270, "graphY": 215},
            {"id": "F", "label": "김포분기", "navX": 665, "navY": 70, "graphX": 385, "graphY": 65},
            {"id": "G", "label": "마곡JC", "navX": 665, "navY": 225, "graphX": 385, "graphY": 215},
            {"id": "H", "label": "공항터미널", "navX": 875, "navY": 150, "graphX": 490, "graphY": 140},
        ],
        "edges": [
            {"u": "A", "v": "B", "w": 6},
            {"u": "A", "v": "C", "w": 3},
            {"u": "B", "v": "D", "w": 4},
            {"u": "C", "v": "D", "w": 5},
            {"u": "C", "v": "E", "w": 2},
            {"u": "D", "v": "E", "w": 2},
            {"u": "D", "v": "F", "w": 7},
            {"u": "E", "v": "G", "w": 6},
            {"u": "F", "v": "G", "w": 2},
            {"u": "F", "v": "H", "w": 5},
            {"u": "G", "v": "H", "w": 3},
            {"u": "B", "v": "F", "w": 12},
        ],
    },
    "logistics_hub": {
        "id": "logistics_hub",
        "name": "스마트 물류 허브망 (A 중앙센터 → G 최종배송)",
        "description": "다중 교차 경로에서 우선순위 큐(Min-Heap)의 최소 비용 선택 원리를 확인하는 네트워크",
        "start": "A",
        "target": "G",
        "nodes": [
            {"id": "A", "label": "중앙센터", "navX": 90, "navY": 150, "graphX": 60, "graphY": 140},
            {"id": "B", "label": "북부허브", "navX": 290, "navY": 65, "graphX": 185, "graphY": 55},
            {"id": "C", "label": "남부허브", "navX": 290, "navY": 235, "graphX": 185, "graphY": 225},
            {"id": "D", "label": "환적기지", "navX": 485, "navY": 150, "graphX": 300, "graphY": 140},
            {"id": "E", "label": "동부거점", "navX": 680, "navY": 65, "graphX": 410, "graphY": 55},
            {"id": "F", "label": "항만터미널", "navX": 680, "navY": 235, "graphX": 410, "graphY": 225},
            {"id": "G", "label": "최종배송", "navX": 870, "navY": 150, "graphX": 485, "graphY": 140},
        ],
        "edges": [
            {"u": "A", "v": "B", "w": 8},
            {"u": "A", "v": "C", "w": 3},
            {"u": "B", "v": "D", "w": 2},
            {"u": "C", "v": "B", "w": 4},
            {"u": "C", "v": "D", "w": 7},
            {"u": "C", "v": "F", "w": 11},
            {"u": "D", "v": "E", "w": 4},
            {"u": "D", "v": "F", "w": 3},
            {"u": "E", "v": "G", "w": 3},
            {"u": "F", "v": "E", "w": 2},
            {"u": "F", "v": "G", "w": 6},
        ],
    },
}


def get_preset_graphs() -> List[Dict[str, Any]]:
    return [
        {
            "id": g["id"],
            "name": g["name"],
            "description": g["description"],
            "start": g["start"],
            "target": g["target"],
            "node_count": len(g["nodes"]),
            "edge_count": len(g["edges"]),
            "nodes": g["nodes"],
            "edges": g["edges"],
        }
        for g in PRESET_GRAPHS.values()
    ]


def generate_random_graph(
    node_count: int = 7, seed: Optional[int] = None
) -> Dict[str, Any]:
    """연결된 무작위 가중치 도로망 그래프를 생성합니다."""
    rng = random.Random(seed)
    n = max(5, min(9, node_count))
    labels = ["출발지", "북측교차", "남측교차", "중앙광장", "동부IC", "서부IC", "역세권", "환승센터", "목적지"]

    # Layered horizontal coordinates for crisp, non-overlapping SVG rendering
    nodes: List[Dict[str, Any]] = []
    for idx in range(n):
        nid = chr(ord("A") + idx)
        if idx == 0:
            nav_x, nav_y, gx, gy = 90, 150, 60, 140
            lbl = "출발지"
        elif idx == n - 1:
            nav_x, nav_y, gx, gy = 870, 150, 485, 140
            lbl = "목적지"
        else:
            col_total = math.ceil((n - 2) / 2)
            col_idx = (idx - 1) // 2
            is_top = (idx - 1) % 2 == 0
            ratio = (col_idx + 1) / (col_total + 1)
            nav_x = int(90 + ratio * 780)
            gx = int(60 + ratio * 425)
            if idx == n - 2 and (n - 2) % 2 == 1:
                nav_y, gy = 150, 140
            else:
                nav_y = 68 if is_top else 232
                gy = 58 if is_top else 222
            lbl = labels[idx] if idx < len(labels) - 1 else f"거점{nid}"
        nodes.append(
            {"id": nid, "label": lbl, "navX": nav_x, "navY": nav_y, "graphX": gx, "graphY": gy}
        )

    edge_set: Set[Tuple[str, str]] = set()
    edges: List[Dict[str, Any]] = []

    def add_edge(u: str, v: str, w: int) -> None:
        key = (u, v) if u < v else (v, u)
        if u != v and key not in edge_set:
            edge_set.add(key)
            edges.append({"u": u, "v": v, "w": w})

    # Backbone spanning chain to guarantee full connectivity
    for i in range(n - 1):
        add_edge(nodes[i]["id"], nodes[i + 1]["id"], rng.randint(2, 9))

    # Add cross/shortcut edges between nearby layers
    for i in range(n):
        for j in range(i + 2, min(n, i + 4)):
            if rng.random() < 0.65:
                add_edge(nodes[i]["id"], nodes[j]["id"], rng.randint(2, 11))

    # Ensure start & target have at least 2 incident edges
    if sum(1 for e in edges if "A" in (e["u"], e["v"])) < 2 and n > 2:
        add_edge("A", "C", rng.randint(2, 8))
    target_id = nodes[-1]["id"]
    if sum(1 for e in edges if target_id in (e["u"], e["v"])) < 2 and n > 2:
        add_edge(nodes[-3]["id"], target_id, rng.randint(2, 8))

    return {
        "id": f"random_{n}n_{len(edges)}e",
        "name": f"랜덤 도로망 그래프 ({nodes[0]['id']} → {target_id}, |V|={n}, |E|={len(edges)})",
        "description": "자동 생성된 연결 가중치 도로망 그래프",
        "start": nodes[0]["id"],
        "target": target_id,
        "node_count": n,
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


def _reconstruct_path(
    prev: Dict[str, Optional[str]], target: str
) -> List[str]:
    path: List[str] = []
    cur: Optional[str] = target
    seen: Set[str] = set()
    while cur is not None and cur not in seen:
        seen.add(cur)
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return path


def run_dijkstra(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    start_id: str,
    target_id: str,
    graph_name: str = "네비게이션 그래프",
) -> Dict[str, Any]:
    """
    다익스트라(Dijkstra) 최단 경로 알고리즘 수행 및 단계별 스냅샷 생성.
    """
    t0 = time.perf_counter()

    node_ids = [n["id"] for n in nodes]
    label_map = {n["id"]: n.get("label", n["id"]) for n in nodes}
    adj: Dict[str, List[Tuple[str, int]]] = {nid: [] for nid in node_ids}
    for e in edges:
        u, v, w = e["u"], e["v"], int(e["w"])
        adj[u].append((v, w))
        adj[v].append((u, w))

    v_total = len(node_ids)
    e_total = len(edges) * 2  # undirected edges checked from both sides max

    dist: Dict[str, float] = {nid: math.inf for nid in node_ids}
    prev: Dict[str, Optional[str]] = {nid: None for nid in node_ids}
    settled: Set[str] = set()
    dist[start_id] = 0

    pq: List[Tuple[float, str]] = [(0, start_id)]
    steps: List[Dict[str, Any]] = []
    ops = 0

    def serialize_distances() -> Dict[str, Optional[int]]:
        return {
            nid: (None if math.isinf(dist[nid]) else int(dist[nid]))
            for nid in node_ids
        }

    def format_pq_preview() -> str:
        candidates = [
            (int(dist[nid]), nid)
            for nid in node_ids
            if nid not in settled and not math.isinf(dist[nid])
        ]
        candidates.sort(key=lambda item: (item[0], item[1]))
        return ", ".join(f"{nid}:{d}" for d, nid in candidates) if candidates else "Empty"

    def build_step_histogram(
        current_node: Optional[str],
        relaxing_neighbors: List[str],
        shortest_path: List[str],
    ) -> Dict[str, Any]:
        """각 단계(Step) 시점의 정점별 최단 거리 d[v] 히스토그램 스냅샷 배열 생성"""
        finite_vals = [int(d) for d in dist.values() if not math.isinf(d) and d > 0]
        max_finite = max(finite_vals) if finite_vals else 1
        relax_set = set(relaxing_neighbors)
        path_set = set(shortest_path) if len(shortest_path) > 1 else set()

        node_bars: List[Dict[str, Any]] = []
        frontier_count = 0
        unvisited_count = 0

        for nid in node_ids:
            d_val = dist[nid]
            is_inf = math.isinf(d_val)
            if nid in path_set:
                bar_status = "path"
            elif nid == current_node:
                bar_status = "current"
            elif nid in relax_set:
                bar_status = "relaxing"
            elif nid in settled:
                bar_status = "settled"
            elif not is_inf:
                bar_status = "frontier"
                frontier_count += 1
            else:
                bar_status = "unvisited"
                unvisited_count += 1

            height_pct = (
                100.0
                if is_inf
                else (8.0 if d_val == 0 else min(95.0, round((d_val / max_finite) * 85.0 + 10.0, 1)))
            )
            node_bars.append(
                {
                    "node": nid,
                    "label": label_map[nid],
                    "distance": None if is_inf else int(d_val),
                    "is_inf": is_inf,
                    "status": bar_status,
                    "height_pct": height_pct,
                }
            )

        return {
            "node_bars": node_bars,
            "summary": {
                "settled_count": len(settled),
                "frontier_count": frontier_count,
                "unvisited_count": unvisited_count,
                "relaxation_ops": ops,
                "max_finite_distance": max_finite,
            },
        }

    def make_snapshot(
        current_node: Optional[str],
        relaxing_neighbors: List[str],
        action_log: str,
        shortest_path: List[str],
    ) -> None:
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 4)
        denom = max(1, v_total + e_total)
        progress_pct = min(100.0, round(((len(settled) + ops) / denom) * 100.0, 1))
        steps.append(
            {
                "stepIndex": len(steps),
                "currentNode": current_node,
                "relaxingNeighbors": list(relaxing_neighbors),
                "distances": serialize_distances(),
                "predecessors": dict(prev),
                "settled": [nid for nid in node_ids if nid in settled],
                "operations": ops,
                "elapsedMs": elapsed_ms,
                "actionLog": action_log,
                "pqPreview": format_pq_preview(),
                "shortestPath": list(shortest_path),
                "histogram": build_step_histogram(
                    current_node, relaxing_neighbors, shortest_path
                ),
                "time_complexity": {
                    "notation": "O((V + E) log V)",
                    "v_total": v_total,
                    "e_total": len(edges),
                    "v_settled": len(settled),
                    "relaxation_ops": ops,
                    "progress_pct": progress_pct,
                },
            }
        )

    make_snapshot(
        current_node=None,
        relaxing_neighbors=[],
        action_log=f"초기화 완료: 시작 정점 {start_id}({label_map[start_id]})의 거리를 0으로 설정",
        shortest_path=[],
    )

    while pq:
        curr_d, u = heapq.heappop(pq)
        if u in settled:
            continue
        if curr_d > dist[u]:
            continue

        settled.add(u)
        updated: List[str] = []

        for v, w in adj[u]:
            if v in settled:
                continue
            ops += 1
            alt = dist[u] + w
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(pq, (alt, v))
                updated.append(v)

        u_label = label_map[u]
        if updated:
            log_msg = f"정점 {u}({u_label}) 확정 → 인접 정점 [{', '.join(updated)}] 최단 거리 갱신"
        else:
            log_msg = f"정점 {u}({u_label}) 확정 → 거리 갱신 없음"

        path: List[str] = []
        if u == target_id or len(settled) == v_total:
            if not math.isinf(dist[target_id]):
                path = _reconstruct_path(prev, target_id)

        make_snapshot(u, updated, log_msg, path)

        if u == target_id:
            break

    total_ms = round((time.perf_counter() - t0) * 1000.0, 4)
    found = not math.isinf(dist[target_id])
    final_path = _reconstruct_path(prev, target_id) if found else []

    return {
        "graph": {
            "name": graph_name,
            "start": start_id,
            "target": target_id,
            "node_count": v_total,
            "edge_count": len(edges),
            "nodes": nodes,
            "edges": edges,
        },
        "summary": {
            "algorithm": "Dijkstra",
            "found": found,
            "shortest_cost": int(dist[target_id]) if found else None,
            "shortest_path": final_path,
            "total_steps": len(steps) - 1,
            "operations": ops,
            "settled_count": len(settled),
            "elapsed_ms": total_ms,
            "time_complexity": "O((V + E) log V)",
        },
        "steps": steps,
    }


if __name__ == "__main__":
    sample = PRESET_GRAPHS["campus_nav"]
    res = run_dijkstra(
        nodes=sample["nodes"],
        edges=sample["edges"],
        start_id=sample["start"],
        target_id=sample["target"],
        graph_name=sample["name"],
    )
    print(
        f"Path={' -> '.join(res['summary']['shortest_path'])}, "
        f"Cost={res['summary']['shortest_cost']}, Ops={res['summary']['operations']}"
    )
