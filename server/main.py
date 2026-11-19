"""
FastAPI Server for BFS vs DFS Maze Escape Visualizer
- Implements BFS (Queue/FIFO) & DFS (Stack/LIFO)
- Generates step-by-step histogram snapshot arrays
- Includes elapsed_ms & O(V + E) time complexity progress metadata
"""

import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from algorithms import (
    PRESET_MAZES,
    compare_bfs_dfs,
    generate_maze,
    get_preset_list,
)

app = FastAPI(
    title="BFS vs DFS Maze Escape API",
    description="너비 우선 탐색(BFS · Queue)과 깊이 우선 탐색(DFS · Stack) 미로탈출 시각화 및 단계별 히스토그램 분석 서버",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SolveMazeRequest(BaseModel):
    preset_id: Optional[str] = Field(
        default=None,
        description="프리셋 미로 ID (grid 미입력 시 사용)",
    )
    maze_name: Optional[str] = Field(
        default=None,
        description="미로 이름",
    )
    grid: Optional[List[List[int]]] = Field(
        default=None,
        description="2차원 미로 격자 (0: 이동 가능, 1: 벽)",
    )
    start: Optional[List[int]] = Field(
        default=None,
        description="시작 좌표 [row, col]",
    )
    goal: Optional[List[int]] = Field(
        default=None,
        description="출구 좌표 [row, col]",
    )


class GenerateMazeRequest(BaseModel):
    rows: int = Field(default=11, ge=7, le=21)
    cols: int = Field(default=11, ge=7, le=21)
    braid_ratio: float = Field(default=0.22, ge=0.0, le=0.5)
    seed: Optional[int] = Field(default=None)


def _validate_maze(
    grid: List[List[int]], start: List[int], goal: List[int]
) -> None:
    if not grid or not grid[0]:
        raise HTTPException(status_code=400, detail="미로 격자(grid)가 비어 있습니다.")

    rows = len(grid)
    cols = len(grid[0])
    if rows > 25 or cols > 25:
        raise HTTPException(status_code=400, detail="미로 크기는 최대 25×25까지 지원합니다.")

    for row in grid:
        if len(row) != cols:
            raise HTTPException(status_code=400, detail="모든 행의 열 길이가 동일해야 합니다.")

    for label, pt in (("start", start), ("goal", goal)):
        if len(pt) != 2:
            raise HTTPException(status_code=400, detail=f"{label} 좌표는 [row, col] 형식이어야 합니다.")
        r, c = pt
        if not (0 <= r < rows and 0 <= c < cols):
            raise HTTPException(status_code=400, detail=f"{label} 좌표가 미로 범위를 벗어났습니다.")
        if grid[r][c] != 0:
            raise HTTPException(status_code=400, detail=f"{label} 위치는 벽(1)이 아닌 이동 가능 칸(0)이어야 합니다.")


@app.get("/")
def read_root() -> Dict[str, Any]:
    return {
        "service": "BFS vs DFS Maze Escape Visualizer API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "presets": "GET /maze/presets",
            "generate": "POST /maze/generate",
            "solve": "POST /solve",
        },
    }


@app.get("/health")
def health_check() -> Dict[str, Any]:
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    return {
        "status": "healthy",
        "service": "bfs-dfs-maze-visualizer",
        "version": "1.0.0",
        "gemini_api_key_configured": bool(gemini_key),
    }


@app.get("/maze/presets")
def maze_presets() -> Dict[str, Any]:
    return {
        "status": "ok",
        "presets": get_preset_list(),
    }


@app.post("/maze/generate")
def maze_generate(req: GenerateMazeRequest) -> Dict[str, Any]:
    maze = generate_maze(
        rows=req.rows,
        cols=req.cols,
        braid_ratio=req.braid_ratio,
        seed=req.seed,
    )
    return {
        "status": "ok",
        "maze": maze,
    }


@app.post("/solve")
def solve_maze(req: SolveMazeRequest) -> Dict[str, Any]:
    """
    동일한 미로에서 BFS(Queue)와 DFS(Stack)를 동시 수행하여
    단계별 히스토그램 스냅샷 배열 및 소요 시간·시간 복잡도 메타데이터를 반환합니다.
    """
    if req.grid is not None:
        grid = req.grid
        start = req.start if req.start is not None else [1, 1]
        goal = req.goal if req.goal is not None else [len(grid) - 2, len(grid[0]) - 2]
        maze_name = req.maze_name or "사용자 편집 미로"
    else:
        preset_key = req.preset_id or "classic_branch"
        preset = PRESET_MAZES.get(preset_key)
        if not preset:
            raise HTTPException(
                status_code=404,
                detail=f"존재하지 않는 preset_id 입니다: {preset_key}",
            )
        grid = preset["grid"]
        start = req.start if req.start is not None else preset["start"]
        goal = req.goal if req.goal is not None else preset["goal"]
        maze_name = req.maze_name or preset["name"]

    _validate_maze(grid, start, goal)

    result = compare_bfs_dfs(
        grid=grid,
        start=(start[0], start[1]),
        goal=(goal[0], goal[1]),
        maze_name=maze_name,
    )
    return {
        "status": "ok",
        "data": result,
    }
