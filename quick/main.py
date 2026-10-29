"""
FastAPI Server for Multi-Sort Algorithm Snapshot Visualizer
Designed for Google Cloud Run deployment & GAS client consumption
"""

import os
import random
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from algorithms import compare_all_sorts, run_shell_sort, run_quick_sort, run_merge_sort

app = FastAPI(
    title="Algorithm Sorting Snapshot API",
    description="Shell Sort, Quick Sort, Merge Sort의 단계별 스냅샷 히스토리를 반환하는 Cloud Run API",
    version="1.0.0",
)

# CORS 설정 (GAS 및 웹 브라우저 클라이언트 허용)
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
        description="정렬할 정수 배열. 생략 시 기본 랜덤 배열(12개)이 자동 생성됩니다.",
    )
    size: Optional[int] = Field(
        default=12,
        ge=3,
        le=50,
        description="랜덤 생성 시 원소 개수 (기본값: 12, 최대: 50)",
    )


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Algorithm Sorting Snapshot Visualizer Server",
        "supported_algorithms": ["shell_sort", "quick_sort", "merge_sort"],
        "endpoints": {
            "health": "/health",
            "sort_all (POST)": "/sort",
            "sort_sample (GET)": "/sort/sample",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/sort/sample")
def sort_sample(size: int = 12):
    """샘플 랜덤 배열을 즉시 정렬하여 스냅샷 히스토리를 반환하는 간편 GET 엔드포인트"""
    sample_size = max(3, min(size, 30))
    array = random.sample(range(5, 100), sample_size)
    return compare_all_sorts(array)


@app.post("/sort")
def sort_algorithms(request: SortRequest):
    """
    3가지 알고리즘(셸, 퀵, 병합)의 스냅샷 히스토리를 한 번에 생성하여 반환합니다.
    """
    if request.array is not None:
        if len(request.array) < 2:
            raise HTTPException(status_code=400, detail="배열 길이는 최소 2개 이상이어야 합니다.")
        if len(request.array) > 60:
            raise HTTPException(status_code=400, detail="시각화 최적화를 위해 원소 개수는 60개 이하로 제한됩니다.")
        array = request.array
    else:
        # 랜덤 배열 생성
        size = request.size or 12
        array = random.sample(range(5, 100), size)

    return compare_all_sorts(array)


if __name__ == "__main__":
    import uvicorn

    # Cloud Run 표준 환경변수 PORT 지원 (기본값: 8080)
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

