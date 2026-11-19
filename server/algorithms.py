"""
BFS (Queue / FIFO) vs DFS (Stack / LIFO) Maze Escape Algorithm Engine
Generates step-by-step snapshots with depth histograms and O(V + E) complexity metadata.
"""

from collections import deque
import random
import time
from typing import Any, Dict, List, Optional, Tuple

Coord = Tuple[int, int]

# Cell values: 0 = walkable path, 1 = wall
DIRECTIONS: List[Tuple[int, int, str]] = [
    (-1, 0, "상"),
    (0, 1, "우"),
    (1, 0, "하"),
    (0, -1, "좌"),
]


PRESET_MAZES: Dict[str, Dict[str, Any]] = {
    "classic_branch": {
        "id": "classic_branch",
        "name": "다중 분기 미로 (기본 · 11×11)",
        "description": "여러 탈출 경로가 공존하여 BFS의 최단 경로 보장과 DFS의 깊은 우회 탐색 차이를 명확히 비교",
        "start": [1, 1],
        "goal": [9, 9],
        "grid": [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
    },
    "open_corridor": {
        "id": "open_corridor",
        "name": "개방형 광장 미로 (11×11)",
        "description": "넓은 공간에서 BFS Queue가 파동처럼 확장되는 모습과 DFS Stack이 직선 깊이로 파고드는 차이 시각화",
        "start": [1, 1],
        "goal": [9, 9],
        "grid": [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
    },
    "dead_end_trap": {
        "id": "dead_end_trap",
        "name": "막다른 길 함정 미로 (13×13)",
        "description": "깊은 막다른 골목이 많아 DFS의 백트래킹(Stack Pop) 동작과 BFS의 레벨별 탐색을 선명하게 대조",
        "start": [1, 1],
        "goal": [11, 11],
        "grid": [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
    },
    "spiral_labyrinth": {
        "id": "spiral_labyrinth",
        "name": "복합 미궁 (13×13)",
        "description": "우회로와 지름길이 섞인 복합 구조에서 탐색 효율과 경로 품질을 종합 분석",
        "start": [1, 1],
        "goal": [6, 6],
        "grid": [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
    },
}


def get_preset_list() -> List[Dict[str, Any]]:
    return [
        {
            "id": p["id"],
            "name": p["name"],
            "description": p["description"],
            "rows": len(p["grid"]),
            "cols": len(p["grid"][0]),
            "start": p["start"],
            "goal": p["goal"],
            "grid": p["grid"],
        }
        for p in PRESET_MAZES.values()
    ]


def generate_maze(
    rows: int = 11,
    cols: int = 11,
    braid_ratio: float = 0.22,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    무작위 풀 수 있는 다중 경로 미로 생성.
    완전 미로(Randomized DFS)를 먼저 생성한 뒤, braid_ratio만큼 내부 벽을 허물어
    BFS 최단 경로와 DFS 우회 경로의 차이가 드러나도록 루프를 추가합니다.
    """
    rows = max(7, min(21, rows if rows % 2 == 1 else rows + 1))
    cols = max(7, min(21, cols if cols % 2 == 1 else cols + 1))
    rng = random.Random(seed)

    grid = [[1 for _ in range(cols)] for _ in range(rows)]
    start = (1, 1)
    goal = (rows - 2, cols - 2)

    grid[start[0]][start[1]] = 0
    stack: List[Coord] = [start]

    while stack:
        r, c = stack[-1]
        neighbors: List[Tuple[int, int, int, int]] = []
        for dr, dc, _ in DIRECTIONS:
            nr, nc = r + dr * 2, c + dc * 2
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and grid[nr][nc] == 1:
                neighbors.append((nr, nc, r + dr, c + dc))
        if neighbors:
            nr, nc, wr, wc = rng.choice(neighbors)
            grid[wr][wc] = 0
            grid[nr][nc] = 0
            stack.append((nr, nc))
        else:
            stack.pop()

    # Add extra openings (loops) so BFS shortest path differs from DFS path
    removable_walls: List[Coord] = []
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if grid[r][c] == 1:
                horiz_open = grid[r][c - 1] == 0 and grid[r][c + 1] == 0
                vert_open = grid[r - 1][c] == 0 and grid[r + 1][c] == 0
                if horiz_open ^ vert_open:
                    removable_walls.append((r, c))

    rng.shuffle(removable_walls)
    open_count = max(2, int(len(removable_walls) * max(0.0, min(0.5, braid_ratio))))
    for r, c in removable_walls[:open_count]:
        grid[r][c] = 0

    grid[start[0]][start[1]] = 0
    grid[goal[0]][goal[1]] = 0

    return {
        "id": f"random_{rows}x{cols}",
        "name": f"랜덤 다중경로 미로 ({rows}×{cols})",
        "description": "자동 생성된 다중 경로 미로 (BFS 최단경로 vs DFS 깊이탐색 비교)",
        "rows": rows,
        "cols": cols,
        "start": [start[0], start[1]],
        "goal": [goal[0], goal[1]],
        "grid": grid,
    }


def _analyze_graph(grid: List[List[int]]) -> Tuple[int, int]:
    """이동 가능한 정점 수(V)와 간선 수(E, 방향 간선 기준) 계산"""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    vertices = 0
    edges = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                vertices += 1
                for dr, dc, _ in DIRECTIONS:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                        edges += 1
    return vertices, edges


def _reconstruct_path(
    parent: Dict[Coord, Optional[Coord]], target: Coord
) -> List[List[int]]:
    path: List[List[int]] = []
    curr: Optional[Coord] = target
    seen = set()
    while curr is not None and curr not in seen:
        seen.add(curr)
        path.append([curr[0], curr[1]])
        curr = parent.get(curr)
    path.reverse()
    return path


def _build_depth_histogram(
    visited_depths: Dict[Coord, int],
    frontier_depths: Dict[Coord, int],
) -> List[Dict[str, int]]:
    """
    각 단계(Step) 시점의 깊이(Depth/Distance)별 방문 노드 및 대기열(Frontier) 분포를
    히스토그램 배열로 생성합니다.
    """
    visited_counts: Dict[int, int] = {}
    frontier_counts: Dict[int, int] = {}

    for d in visited_depths.values():
        visited_counts[d] = visited_counts.get(d, 0) + 1
    for d in frontier_depths.values():
        frontier_counts[d] = frontier_counts.get(d, 0) + 1

    max_depth = 0
    if visited_counts:
        max_depth = max(max_depth, max(visited_counts.keys()))
    if frontier_counts:
        max_depth = max(max_depth, max(frontier_counts.keys()))

    bins: List[Dict[str, int]] = []
    for d in range(max_depth + 1):
        v_cnt = visited_counts.get(d, 0)
        f_cnt = frontier_counts.get(d, 0)
        bins.append(
            {
                "depth": d,
                "visited": v_cnt,
                "frontier": f_cnt,
                "total": v_cnt + f_cnt,
            }
        )
    return bins


def _complexity_meta(
    v_total: int, e_total: int, v_visited: int, e_checked: int
) -> Dict[str, Any]:
    denom = max(1, v_total + e_total)
    progress = min(100.0, round(((v_visited + e_checked) / denom) * 100.0, 1))
    return {
        "notation": "O(V + E)",
        "v_total": v_total,
        "e_total": e_total,
        "v_visited": v_visited,
        "e_checked": e_checked,
        "operations": v_visited + e_checked,
        "progress_pct": progress,
    }


def run_bfs(
    grid: List[List[int]], start: Coord, goal: Coord
) -> Dict[str, Any]:
    """
    너비 우선 탐색 (BFS - Breadth-First Search)
    자료구조: Queue (FIFO - 선입선출)
    특징: 시작점으로부터 거리가 가까운 레벨(Depth)부터 순차 확장하여 최단 탈출 경로 보장
    """
    rows = len(grid)
    cols = len(grid[0])
    v_total, e_total = _analyze_graph(grid)

    t0 = time.perf_counter()

    queue: deque[Coord] = deque([start])
    discovered = {start}
    visited_order: List[List[int]] = []
    visited_depths: Dict[Coord, int] = {}
    frontier_depths: Dict[Coord, int] = {start: 0}
    parent: Dict[Coord, Optional[Coord]] = {start: None}
    depth_map: Dict[Coord, int] = {start: 0}

    steps: List[Dict[str, Any]] = []
    step_idx = 0
    edges_checked = 0
    max_frontier = 1
    found = False
    final_path: List[List[int]] = []

    steps.append(
        {
            "step": step_idx,
            "phase": "INIT",
            "current": [start[0], start[1]],
            "visited": [],
            "frontier": [[start[0], start[1]]],
            "path": [[start[0], start[1]]],
            "current_depth": 0,
            "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 4),
            "time_complexity": _complexity_meta(v_total, e_total, 0, 0),
            "histogram": {
                "depth_bins": _build_depth_histogram(visited_depths, frontier_depths),
                "metrics": {
                    "visited_count": 0,
                    "frontier_count": 1,
                    "current_depth": 0,
                    "edges_checked": 0,
                    "backtracks": 0,
                },
            },
            "trace": f"시작 위치 ({start[0]}, {start[1]})을 Queue(FIFO)에 삽입하며 BFS 탐색 초기화",
        }
    )

    while queue:
        curr = queue.popleft()
        curr_depth = depth_map[curr]
        frontier_depths.pop(curr, None)
        visited_depths[curr] = curr_depth
        visited_order.append([curr[0], curr[1]])
        step_idx += 1

        if curr == goal:
            found = True
            final_path = _reconstruct_path(parent, goal)
            steps.append(
                {
                    "step": step_idx,
                    "phase": "FOUND",
                    "current": [curr[0], curr[1]],
                    "visited": list(visited_order),
                    "frontier": [[r, c] for r, c in queue],
                    "path": final_path,
                    "current_depth": curr_depth,
                    "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 4),
                    "time_complexity": _complexity_meta(
                        v_total, e_total, len(visited_order), edges_checked
                    ),
                    "histogram": {
                        "depth_bins": _build_depth_histogram(
                            visited_depths, frontier_depths
                        ),
                        "metrics": {
                            "visited_count": len(visited_order),
                            "frontier_count": len(queue),
                            "current_depth": curr_depth,
                            "edges_checked": edges_checked,
                            "backtracks": 0,
                        },
                    },
                    "trace": f"출구 ({goal[0]}, {goal[1]}) 도착! 최단 탈출 거리 {len(final_path) - 1}칸 (방문 {len(visited_order)}칸)",
                }
            )
            break

        enqueued_labels: List[str] = []
        for dr, dc, dname in DIRECTIONS:
            nr, nc = curr[0] + dr, curr[1] + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                edges_checked += 1
                nxt = (nr, nc)
                if nxt not in discovered:
                    discovered.add(nxt)
                    parent[nxt] = curr
                    depth_map[nxt] = curr_depth + 1
                    frontier_depths[nxt] = curr_depth + 1
                    queue.append(nxt)
                    enqueued_labels.append(f"{dname}({nr},{nc})")

        max_frontier = max(max_frontier, len(queue))
        phase = "EXPLORE" if enqueued_labels else "DEAD_END"
        if enqueued_labels:
            trace = (
                f"Queue Front ({curr[0]},{curr[1]}) [Depth {curr_depth}] Dequeue → "
                f"Rear Enqueue: {', '.join(enqueued_labels)}"
            )
        else:
            trace = (
                f"Queue Front ({curr[0]},{curr[1]}) [Depth {curr_depth}] Dequeue → "
                f"추가 확장 가능한 미방문 인접 칸 없음"
            )

        steps.append(
            {
                "step": step_idx,
                "phase": phase,
                "current": [curr[0], curr[1]],
                "visited": list(visited_order),
                "frontier": [[r, c] for r, c in queue],
                "path": _reconstruct_path(parent, curr),
                "current_depth": curr_depth,
                "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 4),
                "time_complexity": _complexity_meta(
                    v_total, e_total, len(visited_order), edges_checked
                ),
                "histogram": {
                    "depth_bins": _build_depth_histogram(
                        visited_depths, frontier_depths
                    ),
                    "metrics": {
                        "visited_count": len(visited_order),
                        "frontier_count": len(queue),
                        "current_depth": curr_depth,
                        "edges_checked": edges_checked,
                        "backtracks": 0,
                    },
                },
                "trace": trace,
            }
        )

    if not found:
        step_idx += 1
        steps.append(
            {
                "step": step_idx,
                "phase": "NO_PATH",
                "current": [start[0], start[1]],
                "visited": list(visited_order),
                "frontier": [],
                "path": [],
                "current_depth": 0,
                "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 4),
                "time_complexity": _complexity_meta(
                    v_total, e_total, len(visited_order), edges_checked
                ),
                "histogram": {
                    "depth_bins": _build_depth_histogram(
                        visited_depths, frontier_depths
                    ),
                    "metrics": {
                        "visited_count": len(visited_order),
                        "frontier_count": 0,
                        "current_depth": 0,
                        "edges_checked": edges_checked,
                        "backtracks": 0,
                    },
                },
                "trace": "Queue가 비어 탐색을 종료했습니다. 출구로 가는 경로가 존재하지 않습니다.",
            }
        )

    total_ms = round((time.perf_counter() - t0) * 1000.0, 4)

    return {
        "algorithm": "BFS",
        "title": "너비 우선 탐색 (BFS)",
        "data_structure": "Queue (FIFO)",
        "summary": {
            "found": found,
            "total_steps": len(steps) - 1,
            "visited_count": len(visited_order),
            "path_length": max(0, len(final_path) - 1) if found else 0,
            "path": final_path,
            "max_frontier_size": max_frontier,
            "edges_checked": edges_checked,
            "backtrack_count": 0,
            "elapsed_ms": total_ms,
            "time_complexity": "O(V + E)",
            "space_complexity": "O(V) (레벨 너비 비례)",
            "guarantees_shortest_path": True,
        },
        "steps": steps,
    }


def run_dfs(
    grid: List[List[int]], start: Coord, goal: Coord
) -> Dict[str, Any]:
    """
    깊이 우선 탐색 (DFS - Depth-First Search)
    자료구조: Stack (LIFO - 후입선출)
    특징: 한 분기를 끝까지 깊게 탐색한 뒤 막다른 길에서 Stack을 통해 백트래킹
    """
    rows = len(grid)
    cols = len(grid[0])
    v_total, e_total = _analyze_graph(grid)

    t0 = time.perf_counter()

    stack: List[Coord] = [start]
    visited_set = set()
    visited_order: List[List[int]] = []
    visited_depths: Dict[Coord, int] = {}
    frontier_depths: Dict[Coord, int] = {start: 0}
    parent: Dict[Coord, Optional[Coord]] = {start: None}
    depth_map: Dict[Coord, int] = {start: 0}

    steps: List[Dict[str, Any]] = []
    step_idx = 0
    edges_checked = 0
    max_frontier = 1
    backtrack_count = 0
    found = False
    final_path: List[List[int]] = []

    steps.append(
        {
            "step": step_idx,
            "phase": "INIT",
            "current": [start[0], start[1]],
            "visited": [],
            "frontier": [[start[0], start[1]]],
            "path": [[start[0], start[1]]],
            "current_depth": 0,
            "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 4),
            "time_complexity": _complexity_meta(v_total, e_total, 0, 0),
            "histogram": {
                "depth_bins": _build_depth_histogram(visited_depths, frontier_depths),
                "metrics": {
                    "visited_count": 0,
                    "frontier_count": 1,
                    "current_depth": 0,
                    "edges_checked": 0,
                    "backtracks": 0,
                },
            },
            "trace": f"시작 위치 ({start[0]}, {start[1]})을 Stack(LIFO)에 Push하며 DFS 탐색 초기화",
        }
    )

    while stack:
        curr = stack.pop()
        if curr in visited_set:
            frontier_depths.pop(curr, None)
            continue

        visited_set.add(curr)
        curr_depth = depth_map[curr]
        frontier_depths.pop(curr, None)
        visited_depths[curr] = curr_depth
        visited_order.append([curr[0], curr[1]])
        step_idx += 1

        if curr == goal:
            found = True
            final_path = _reconstruct_path(parent, goal)
            steps.append(
                {
                    "step": step_idx,
                    "phase": "FOUND",
                    "current": [curr[0], curr[1]],
                    "visited": list(visited_order),
                    "frontier": [[r, c] for r, c in stack if (r, c) not in visited_set],
                    "path": final_path,
                    "current_depth": curr_depth,
                    "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 4),
                    "time_complexity": _complexity_meta(
                        v_total, e_total, len(visited_order), edges_checked
                    ),
                    "histogram": {
                        "depth_bins": _build_depth_histogram(
                            visited_depths, frontier_depths
                        ),
                        "metrics": {
                            "visited_count": len(visited_order),
                            "frontier_count": len(
                                [c for c in stack if c not in visited_set]
                            ),
                            "current_depth": curr_depth,
                            "edges_checked": edges_checked,
                            "backtracks": backtrack_count,
                        },
                    },
                    "trace": f"출구 ({goal[0]}, {goal[1]}) 도착! 탐색 경로 길이 {len(final_path) - 1}칸 (방문 {len(visited_order)}칸, 백트래킹 {backtrack_count}회)",
                }
            )
            break

        pushed_labels: List[str] = []
        # Reverse push so Top of Stack follows 상->우->하->좌 priority
        for dr, dc, dname in reversed(DIRECTIONS):
            nr, nc = curr[0] + dr, curr[1] + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                edges_checked += 1
                nxt = (nr, nc)
                if nxt not in visited_set:
                    parent[nxt] = curr
                    depth_map[nxt] = curr_depth + 1
                    frontier_depths[nxt] = curr_depth + 1
                    stack.append(nxt)
                    pushed_labels.append(f"{dname}({nr},{nc})")

        active_frontier = [[r, c] for r, c in stack if (r, c) not in visited_set]
        max_frontier = max(max_frontier, len(active_frontier))

        if pushed_labels:
            phase = "EXPLORE"
            trace = (
                f"Stack Top ({curr[0]},{curr[1]}) [Depth {curr_depth}] Pop → "
                f"Stack Push: {', '.join(pushed_labels)}"
            )
        else:
            backtrack_count += 1
            phase = "BACKTRACK"
            trace = (
                f"막다른 길 ({curr[0]},{curr[1]}) [Depth {curr_depth}] 도달 → "
                f"Stack 이전 분기로 백트래킹 (누적 {backtrack_count}회)"
            )

        steps.append(
            {
                "step": step_idx,
                "phase": phase,
                "current": [curr[0], curr[1]],
                "visited": list(visited_order),
                "frontier": active_frontier,
                "path": _reconstruct_path(parent, curr),
                "current_depth": curr_depth,
                "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 4),
                "time_complexity": _complexity_meta(
                    v_total, e_total, len(visited_order), edges_checked
                ),
                "histogram": {
                    "depth_bins": _build_depth_histogram(
                        visited_depths, frontier_depths
                    ),
                    "metrics": {
                        "visited_count": len(visited_order),
                        "frontier_count": len(active_frontier),
                        "current_depth": curr_depth,
                        "edges_checked": edges_checked,
                        "backtracks": backtrack_count,
                    },
                },
                "trace": trace,
            }
        )

    if not found:
        step_idx += 1
        steps.append(
            {
                "step": step_idx,
                "phase": "NO_PATH",
                "current": [start[0], start[1]],
                "visited": list(visited_order),
                "frontier": [],
                "path": [],
                "current_depth": 0,
                "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 4),
                "time_complexity": _complexity_meta(
                    v_total, e_total, len(visited_order), edges_checked
                ),
                "histogram": {
                    "depth_bins": _build_depth_histogram(
                        visited_depths, frontier_depths
                    ),
                    "metrics": {
                        "visited_count": len(visited_order),
                        "frontier_count": 0,
                        "current_depth": 0,
                        "edges_checked": edges_checked,
                        "backtracks": backtrack_count,
                    },
                },
                "trace": "Stack이 비어 탐색을 종료했습니다. 출구로 가는 경로가 존재하지 않습니다.",
            }
        )

    total_ms = round((time.perf_counter() - t0) * 1000.0, 4)

    return {
        "algorithm": "DFS",
        "title": "깊이 우선 탐색 (DFS)",
        "data_structure": "Stack (LIFO)",
        "summary": {
            "found": found,
            "total_steps": len(steps) - 1,
            "visited_count": len(visited_order),
            "path_length": max(0, len(final_path) - 1) if found else 0,
            "path": final_path,
            "max_frontier_size": max_frontier,
            "edges_checked": edges_checked,
            "backtrack_count": backtrack_count,
            "elapsed_ms": total_ms,
            "time_complexity": "O(V + E)",
            "space_complexity": "O(H) (최대 탐색 깊이 비례)",
            "guarantees_shortest_path": False,
        },
        "steps": steps,
    }


def compare_bfs_dfs(
    grid: List[List[int]],
    start: Coord,
    goal: Coord,
    maze_name: str = "사용자 미로",
) -> Dict[str, Any]:
    """BFS와 DFS를 동일 미로에서 실행하고 단계별 스냅샷·히스토그램·성능 비교 결과를 반환"""
    v_total, e_total = _analyze_graph(grid)
    bfs_result = run_bfs(grid, start, goal)
    dfs_result = run_dfs(grid, start, goal)

    b_sum = bfs_result["summary"]
    d_sum = dfs_result["summary"]

    if b_sum["found"] and d_sum["found"]:
        if b_sum["path_length"] < d_sum["path_length"]:
            shortest_winner = "BFS"
        elif d_sum["path_length"] < b_sum["path_length"]:
            shortest_winner = "DFS"
        else:
            shortest_winner = "TIE"
    else:
        shortest_winner = "NONE"

    if b_sum["visited_count"] < d_sum["visited_count"]:
        fewer_visits = "BFS"
    elif d_sum["visited_count"] < b_sum["visited_count"]:
        fewer_visits = "DFS"
    else:
        fewer_visits = "TIE"

    if b_sum["max_frontier_size"] < d_sum["max_frontier_size"]:
        lower_memory = "BFS"
    elif d_sum["max_frontier_size"] < b_sum["max_frontier_size"]:
        lower_memory = "DFS"
    else:
        lower_memory = "TIE"

    return {
        "maze": {
            "name": maze_name,
            "rows": len(grid),
            "cols": len(grid[0]),
            "grid": grid,
            "start": [start[0], start[1]],
            "goal": [goal[0], goal[1]],
            "walkable_cells": v_total,
            "total_edges": e_total,
        },
        "bfs": bfs_result,
        "dfs": dfs_result,
        "comparison": {
            "shortest_path_winner": shortest_winner,
            "fewer_visits_winner": fewer_visits,
            "lower_memory_winner": lower_memory,
            "path_length_diff": d_sum["path_length"] - b_sum["path_length"],
            "visited_diff": d_sum["visited_count"] - b_sum["visited_count"],
            "max_frontier_diff": b_sum["max_frontier_size"] - d_sum["max_frontier_size"],
            "feature_matrix": [
                {
                    "feature": "핵심 자료구조",
                    "bfs": "Queue (FIFO · 선입선출)",
                    "dfs": "Stack (LIFO · 후입선출)",
                },
                {
                    "feature": "탐색 확장 방식",
                    "bfs": "시작점 기준 레벨(거리)별 동심원 확장",
                    "dfs": "한 분기를 끝까지 파고든 후 백트래킹",
                },
                {
                    "feature": "최단 경로 보장",
                    "bfs": "보장 (가중치 없는 미로에서 항상 최단)",
                    "dfs": "미보장 (먼저 도달한 깊은 경로 반환)",
                },
                {
                    "feature": "시간 복잡도",
                    "bfs": "O(V + E)",
                    "dfs": "O(V + E)",
                },
                {
                    "feature": "메모리(공간) 특성",
                    "bfs": f"최대 Queue {b_sum['max_frontier_size']}칸 (너비에 비례)",
                    "dfs": f"최대 Stack {d_sum['max_frontier_size']}칸 (깊이에 비례)",
                },
                {
                    "feature": "미로 탈출 결과",
                    "bfs": f"경로 {b_sum['path_length']}칸 / 방문 {b_sum['visited_count']}칸",
                    "dfs": f"경로 {d_sum['path_length']}칸 / 방문 {d_sum['visited_count']}칸 (백트래킹 {d_sum['backtrack_count']}회)",
                },
            ],
        },
    }
