"""
FastAPI Server for Boyer-Moore String Search Algorithm Visualizer
Comparing:
- 나쁜 문자 이동법 (Bad Character Rule)
- 착한 접미부 이동법 (Good Suffix Rule & Full Boyer-Moore)
"""

import os
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from algorithms import (
    compare_boyer_moore,
    run_boyer_moore_bad_char,
    run_boyer_moore_good_suffix,
    build_bad_character_table,
)

app = FastAPI(
    title="Boyer-Moore String Search API",
    description="보이어-무어 문자열 탐색 알고리즘 시각화 및 비교 분석 서버 (나쁜 문자표 vs 착한 접미부)",
    version="1.0.0",
)

# Enable CORS for Google Apps Script & web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    text: Optional[str] = Field(
        default="GCATGCGTAGGTAGCGTAGAG",
        description="전체 원본 텍스트 (DNA 염기서열, 영문, 한글 등)",
    )
    pattern: Optional[str] = Field(
        default="GCGTAG",
        description="탐색할 패턴 문자열",
    )


@app.get("/")
def read_root() -> Dict[str, Any]:
    return {
        "service": "Boyer-Moore String Search Engine",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "search": "POST /search",
            "sample": "GET /search/sample",
            "presets": "GET /search/presets",
        },
    }


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {
        "status": "healthy",
        "service": "boyer-moore-search-engine",
        "version": "1.0.0",
    }


@app.get("/search/presets")
def get_presets() -> List[Dict[str, str]]:
    """테스트용 프리셋 목록 제공"""
    return [
        {
            "id": "dna",
            "name": "DNA 염기서열 분석 (기본)",
            "text": "GCATGCGTAGGTAGCGTAGAG",
            "pattern": "GCGTAG",
            "description": "생물 정보학에서 자주 사용되는 DNA 4진 염기서열 매칭",
        },
        {
            "id": "repeated",
            "name": "반복 문자열 (착한 접미부 우세)",
            "text": "BAAAAAABAAAAABAAAAAAB",
            "pattern": "AAAAAB",
            "description": "접미부 일치가 잦아 착한 접미부 규칙이 월등히 빠른 이동을 보이는 예제",
        },
        {
            "id": "english",
            "name": "영문 문장 탐색",
            "text": "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG QUICKLY",
            "pattern": "QUICK",
            "description": "일반 영문 텍스트 내 단어 출현 위치 탐색",
        },
        {
            "id": "worst_case",
            "name": "최악 케이스 (단순 나쁜문자 비교)",
            "text": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            "pattern": "AAAAAB",
            "description": "불일치가 앞쪽에서 발생하여 착한 접미부 점프 차이가 극대화되는 케이스",
        },
        {
            "id": "korean",
            "name": "한글 문자열 탐색",
            "text": "동해물과 백두산이 마르고 닳도록 하느님이 보우하사 우리나라 만세 백두산 만세",
            "pattern": "백두산",
            "description": "유니코드 한글 텍스트에서도 정상 동작하는 탐색",
        },
    ]


@app.post("/search")
def search(req: SearchRequest) -> Dict[str, Any]:
    """
    보이어-무어 나쁜 문자표 & 착한 접미부 동시 실행 및 단계별 스냅샷/성능 비교 결과 반환
    """
    text = (req.text or "").strip()
    pattern = (req.pattern or "").strip()

    if not text:
        raise HTTPException(status_code=400, detail="텍스트(text)를 입력해 주세요.")
    if not pattern:
        raise HTTPException(status_code=400, detail="패턴(pattern)을 입력해 주세요.")
    if len(pattern) > len(text):
        raise HTTPException(
            status_code=400,
            detail="패턴 길이가 텍스트 길이보다 길 수 없습니다.",
        )

    try:
        result = compare_boyer_moore(text, pattern)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"탐색 수행 중 오류 발생: {str(e)}")


@app.get("/search/sample")
def search_sample() -> Dict[str, Any]:
    """기본 샘플 데이터로 즉시 비교 실행"""
    return compare_boyer_moore()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

