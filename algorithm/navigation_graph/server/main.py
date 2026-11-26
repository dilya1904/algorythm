"""
FastAPI Server for DijkstraLab Navigation Graph Visualizer
- Follows $same-folder-py-import (path guard + explicit import + __main__ guard)
- Follows $gas-python-startup-link (GET /health + GAS domain CORS)
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

_CURRENT_DIR = Path(__file__).resolve().parent
if str(_CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(_CURRENT_DIR))

from dijkstra import (
    PRESET_GRAPHS,
    generate_random_graph,
    get_preset_graphs,
    run_dijkstra,
)

app = FastAPI(
    title="DijkstraLab Navigation Graph API",
    description="다익스트라(Dijkstra) 최단 경로 네비게이션 시각화 및 단계별 완화(Relaxation) 분석 서버",
    version="1.0.0",
)

ALLOWED_ORIGINS = [
    "https://script.google.com",
    "https://script.googleusercontent.com",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GraphNode(BaseModel):
    id: str
    label: str
    navX: float
    navY: float
    graphX: float
    graphY: float


class GraphEdge(BaseModel):
    u: str
    v: str
    w: int = Field(ge=1)


class GenerateGraphRequest(BaseModel):
    node_count: int = Field(default=7, ge=5, le=9)
    seed: Optional[int] = Field(default=None)


class SolveDijkstraRequest(BaseModel):
    preset_id: Optional[str] = Field(default=None)
    graph_name: Optional[str] = Field(default=None)
    nodes: Optional[List[GraphNode]] = Field(default=None)
    edges: Optional[List[GraphEdge]] = Field(default=None)
    start: Optional[str] = Field(default=None)
    target: Optional[str] = Field(default=None)


@app.get("/")
def read_root() -> Dict[str, Any]:
    return {
        "service": "DijkstraLab Navigation Graph API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "presets": "GET /graph/presets",
            "generate": "POST /graph/generate",
            "solve": "POST /dijkstra/solve",
        },
    }


@app.get("/health")
def health_check() -> Dict[str, Any]:
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    return {
        "status": "healthy",
        "connected": True,
        "service": "navigation-graph-dijkstra",
        "version": "1.0.0",
        "gemini_api_key_configured": bool(gemini_key),
    }


@app.get("/graph/presets")
def graph_presets() -> Dict[str, Any]:
    return {
        "status": "ok",
        "presets": get_preset_graphs(),
    }


@app.post("/graph/generate")
def graph_generate(req: GenerateGraphRequest) -> Dict[str, Any]:
    graph = generate_random_graph(node_count=req.node_count, seed=req.seed)
    return {
        "status": "ok",
        "graph": graph,
    }


@app.post("/dijkstra/solve")
def solve_dijkstra(req: SolveDijkstraRequest) -> Dict[str, Any]:
    if req.nodes is not None and req.edges is not None:
        nodes = [n.model_dump() for n in req.nodes]
        edges = [e.model_dump() for e in req.edges]
        node_ids = {n["id"] for n in nodes}
        if not nodes:
            raise HTTPException(status_code=400, detail="정점(nodes) 목록이 비어 있습니다.")
        start_id = req.start or nodes[0]["id"]
        target_id = req.target or nodes[-1]["id"]
        if start_id not in node_ids or target_id not in node_ids:
            raise HTTPException(status_code=400, detail="start 또는 target 정점이 nodes에 존재하지 않습니다.")
        for e in edges:
            if e["u"] not in node_ids or e["v"] not in node_ids:
                raise HTTPException(status_code=400, detail="간선의 정점이 nodes에 존재하지 않습니다.")
            if e["w"] <= 0:
                raise HTTPException(status_code=400, detail="다익스트라 알고리즘은 양수 가중치만 지원합니다.")
        graph_name = req.graph_name or "사용자 그래프"
    else:
        preset_key = req.preset_id or "campus_nav"
        preset = PRESET_GRAPHS.get(preset_key)
        if not preset:
            raise HTTPException(status_code=404, detail=f"존재하지 않는 preset_id 입니다: {preset_key}")
        nodes = preset["nodes"]
        edges = preset["edges"]
        start_id = req.start or preset["start"]
        target_id = req.target or preset["target"]
        graph_name = req.graph_name or preset["name"]

    result = run_dijkstra(
        nodes=nodes,
        edges=edges,
        start_id=start_id,
        target_id=target_id,
        graph_name=graph_name,
    )
    return {
        "status": "ok",
        "data": result,
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
