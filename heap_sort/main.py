"""
FastAPI Server for Heap Sort vs Counting Sort Benchmark Lab
Stitch Project: projects/9894791412803030970 (Dual Sort Visualizer Dashboard)
Designed for Google Cloud Run deployment & GAS client consumption
"""

import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from algorithms import (
    compare_heap_and_counting,
    run_heap_sort,
    run_counting_sort,
)

app = FastAPI(
    title="Dual Sort Visualizer API (Heap vs Counting)",
    description="힙 정렬과 도수 정렬의 단계별 스냅샷 히스토리 및 성능 벤치마크를 제공하는 Cloud Run API",
    version="1.0.0",
)

# CORS 설정 (GAS Web App 및 로컬 HTML 클라이언트 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SortRequest(BaseModel):
    array: Optional[List[int]] = Field(
        default=None,
        description="정렬할 정수 배열. 생략 시 기본 랜덤 배열(N=50)이 자동 생성됩니다.",
    )
    size: Optional[int] = Field(
        default=50,
        ge=5,
        le=200,
        description="랜덤 생성 시 원소 개수 (기본값: 50, 범위: 5~200)",
    )


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Dual Sort Visualizer API (Heap vs Counting Sort)",
        "stitch_project": "projects/9894791412803030970",
        "supported_algorithms": ["heap_sort", "counting_sort"],
        "endpoints": {
            "health": "/health",
            "sort_all (POST)": "/sort",
            "sort_sample (GET)": "/sort/sample",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "heap_counting_sort_server",
        "version": "1.0.0",
    }


@app.post("/sort")
def sort_comparison(req: SortRequest):
    """
    힙 정렬과 도수 정렬을 동시 실행하여 스냅샷 히스토리와 벤치마크 지표를 반환합니다.
    """
    try:
        result = compare_heap_and_counting(
            initial_array=req.array,
            size=req.size or 50,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sorting execution error: {str(e)}")


@app.get("/sort/sample")
def sort_sample():
    """기본 규격(N=50)의 샘플 정렬 비교 데이터를 즉시 반환합니다."""
    return compare_heap_and_counting(initial_array=None, size=50)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

