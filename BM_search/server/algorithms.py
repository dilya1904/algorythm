"""
Boyer-Moore String Search Algorithm Engine with Step-by-Step Snapshots
Comparing:
1. 나쁜 문자 이동법 (Bad Character Rule)
2. 착한 접미부 이동법 (Good Suffix Rule & Full Boyer-Moore)

시간 복잡도:
- 최선의 경우(Best): O(N / M) - 불일치 시 패턴 길이만큼 건너뜀
- 평균의 경우(Average): O(N)
- 최악의 경우(Worst): O(N * M) (단순 나쁜문자 단독 시) / O(N) (착한 접미부 적용 시 O(3N))
공간 복잡도: O(M + Σ) (알파벳 크기 + 패턴 길이 테이블)
"""

import copy
import time
from typing import List, Dict, Any, Optional


def build_bad_character_table(pattern: str) -> Dict[str, int]:
    """나쁜 문자표 (Bad Character Table) 생성: 각 문자의 패턴 내 마지막 등장 인덱스 기록"""
    table = {}
    for idx, char in enumerate(pattern):
        table[char] = idx
    return table


def compute_good_suffix_shift(pattern: str, mismatch_j: int) -> int:
    """
    착한 접미부 이동 거리 계산 (Good Suffix Heuristic)
    - mismatch_j: 패턴 내 불일치가 발생한 인덱스 (0 <= mismatch_j < m)
    - 일치한 접미부: pattern[mismatch_j + 1 : m]
    """
    m = len(pattern)
    matched_len = m - 1 - mismatch_j
    if matched_len <= 0:
        return 0  # 일치한 접미부가 없는 경우(첫 비교 불일치)는 0 반환

    suffix = pattern[mismatch_j + 1 :]

    # Case 1: 패턴 앞부분에서 동일한 접미부를 가지며, 바로 앞 문자는 다른 부분 문자열 탐색
    for start in range(m - matched_len - 1, -1, -1):
        if pattern[start : start + matched_len] == suffix:
            if start == 0 or pattern[start - 1] != pattern[mismatch_j]:
                return (mismatch_j + 1) - start

    # Case 2: 일치한 접미부의 일부분(접미부의 접미부)이 패턴의 접두부(Prefix)와 일치하는 경우
    for length in range(matched_len - 1, 0, -1):
        if pattern.startswith(suffix[-length:]):
            return m - length

    # Case 3: 일치하는 부분이 전혀 없는 경우 패턴 전체 길이만큼 이동
    return m


def text_to_histogram_array(text: str) -> List[int]:
    """문자열의 각 문자를 20~95 범위의 히스토그램 막대 높이 값으로 변환"""
    if not text:
        return []
    ord_vals = [ord(c) for c in text]
    min_ord = min(ord_vals)
    max_ord = max(ord_vals)
    if min_ord == max_ord:
        return [60] * len(text)
    return [int(20 + ((v - min_ord) / (max_ord - min_ord)) * 75) for v in ord_vals]


def create_snapshot(
    step: int,
    text: str,
    pattern: str,
    text_offset: int,
    pattern_idx: int,
    phase: str,
    phase_name: str,
    description: str,
    active_indices: Optional[List[int]] = None,
    matched_indices: Optional[List[int]] = None,
    found_indices: Optional[List[int]] = None,
    comparisons: int = 0,
    shifts: int = 0,
    operations: int = 0,
    shift_amount: int = 0,
    elapsed_time_ms: float = 0.0,
    complexity_metric: Optional[Dict[str, Any]] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """보이어-무어 단계별 스냅샷 생성 헬퍼"""
    snapshot = {
        "step": step,
        "text": text,
        "pattern": pattern,
        "text_offset": text_offset,
        "pattern_idx": pattern_idx,
        "text_idx": text_offset + pattern_idx if pattern_idx >= 0 else text_offset,
        "phase": phase,
        "phase_name": phase_name,
        "description": description,
        "active_indices": active_indices or [],
        "matched_indices": matched_indices or [],
        "found_indices": found_indices or [],
        "comparisons": comparisons,
        "shifts": shifts,
        "operations": operations,
        "shift_amount": shift_amount,
        "elapsed_time_ms": elapsed_time_ms,
        "array": text_to_histogram_array(text),
        "time_complexity": complexity_metric or {},
    }
    if extra:
        snapshot.update(extra)
    return snapshot


def run_boyer_moore_bad_char(text: str, pattern: str) -> Dict[str, Any]:
    """
    나쁜 문자 이동법 (Bad Character Rule Only)
    - 우측 끝에서 좌측 방향으로 문자 비교
    - 불일치 발생 시 나쁜 문자표의 마지막 등장 위치를 기준으로 건너뜀
    """
    n, m = len(text), len(pattern)
    history: List[Dict[str, Any]] = []
    comparisons = 0
    shifts = 0
    step = 0
    found_matches: List[int] = []

    start_time = time.perf_counter()

    def get_elapsed() -> float:
        return round((time.perf_counter() - start_time) * 1000, 3)

    if n == 0 or m == 0 or m > n:
        return {
            "algorithm": "bm_bad_character",
            "name_ko": "보이어-무어 : 나쁜 문자표 (Bad Character)",
            "text": text,
            "pattern": pattern,
            "matches": [],
            "comparisons": 0,
            "shifts": 0,
            "operations": 0,
            "execution_time_ms": 0.0,
            "history": [],
            "bad_char_table": {},
        }

    bc_table = build_bad_character_table(pattern)

    # 초기 상태 스냅샷
    history.append(
        create_snapshot(
            step=step,
            text=text,
            pattern=pattern,
            text_offset=0,
            pattern_idx=m - 1,
            phase="init",
            phase_name="탐색 대기 (Ready)",
            description=f"[나쁜 문자표 탐색 시작] 텍스트 길이 {n}, 패턴 길이 {m}",
            active_indices=[m - 1],
            comparisons=0,
            shifts=0,
            operations=0,
            elapsed_time_ms=0.0,
            complexity_metric={
                "formula": "O(N / M) ~ O(N * M)",
                "progress_pct": 0.0,
                "stage": "나쁜 문자표 전처리 완료",
            },
            extra={"bad_char_table": bc_table},
        )
    )

    i = 0
    while i <= n - m:
        j = m - 1
        current_matched: List[int] = []

        while j >= 0:
            comparisons += 1
            step += 1
            text_pos = i + j
            active = [text_pos]

            if pattern[j] == text[text_pos]:
                current_matched.append(text_pos)
                progress = min(99.0, round(((i + (m - 1 - j)) / n) * 100, 1))

                history.append(
                    create_snapshot(
                        step=step,
                        text=text,
                        pattern=pattern,
                        text_offset=i,
                        pattern_idx=j,
                        phase="match_char",
                        phase_name="문자 일치 (Match)",
                        description=f"일치 확인: Text[{text_pos}]('{text[text_pos]}') == Pattern[{j}]('{pattern[j]}')",
                        active_indices=active,
                        matched_indices=copy.copy(current_matched),
                        found_indices=copy.copy(found_matches),
                        comparisons=comparisons,
                        shifts=shifts,
                        operations=comparisons + shifts,
                        elapsed_time_ms=get_elapsed(),
                        complexity_metric={
                            "formula": "O(N / M) ~ O(N * M)",
                            "progress_pct": progress,
                            "stage": f"패턴 뒤에서 {m - 1 - j + 1}번째 문자 일치",
                        },
                    )
                )
                j -= 1
            else:
                # 불일치 발생 (Mismatch)
                mismatched_char = text[text_pos]
                last_pos = bc_table.get(mismatched_char, -1)
                shift = max(1, j - last_pos)

                step += 1
                progress = min(99.0, round((i / max(1, n - m)) * 100, 1))

                desc = (
                    f"불일치! Text[{text_pos}]='{mismatched_char}' != Pattern[{j}]='{pattern[j]}'. "
                    f"나쁜 문자 '{mismatched_char}'의 패턴 내 위치: {last_pos} -> {shift}칸 이동"
                )

                history.append(
                    create_snapshot(
                        step=step,
                        text=text,
                        pattern=pattern,
                        text_offset=i,
                        pattern_idx=j,
                        phase="mismatch",
                        phase_name="불일치 (Mismatch)",
                        description=desc,
                        active_indices=[text_pos],
                        matched_indices=copy.copy(current_matched),
                        found_indices=copy.copy(found_matches),
                        comparisons=comparisons,
                        shifts=shifts,
                        operations=comparisons + shifts,
                        shift_amount=shift,
                        elapsed_time_ms=get_elapsed(),
                        complexity_metric={
                            "formula": "O(N / M) ~ O(N * M)",
                            "progress_pct": progress,
                            "stage": f"나쁜 문자 규칙에 따라 {shift}칸 점프",
                        },
                        extra={
                            "bad_char": mismatched_char,
                            "last_idx_in_pattern": last_pos,
                        },
                    )
                )

                i += shift
                shifts += 1
                break

        if j < 0:
            # 패턴 전체 일치 성공!
            found_matches.append(i)
            step += 1
            progress = min(100.0, round(((i + m) / n) * 100, 1))

            history.append(
                create_snapshot(
                    step=step,
                    text=text,
                    pattern=pattern,
                    text_offset=i,
                    pattern_idx=0,
                    phase="found",
                    phase_name="패턴 발견 (Found!)",
                    description=f"🎉 패턴 발견! 인덱스 [{i} ~ {i + m - 1}] 구간 일치",
                    active_indices=list(range(i, i + m)),
                    matched_indices=list(range(i, i + m)),
                    found_indices=copy.copy(found_matches),
                    comparisons=comparisons,
                    shifts=shifts,
                    operations=comparisons + shifts,
                    shift_amount=1,
                    elapsed_time_ms=get_elapsed(),
                    complexity_metric={
                        "formula": "O(N / M) ~ O(N * M)",
                        "progress_pct": progress,
                        "stage": f"일치 인덱스 {i} 등록 후 다음 탐색",
                    },
                )
            )
            i += 1
            shifts += 1

    end_time = time.perf_counter()
    execution_time_ms = round((end_time - start_time) * 1000, 3)

    # 최종 완료
    step += 1
    history.append(
        create_snapshot(
            step=step,
            text=text,
            pattern=pattern,
            text_offset=n,
            pattern_idx=-1,
            phase="completed",
            phase_name="탐색 완료 (Completed)",
            description=f"나쁜 문자표 탐색 완료! 총 {len(found_matches)}개 매칭 발견 (비교 {comparisons}회, 이동 {shifts}회)",
            found_indices=copy.copy(found_matches),
            comparisons=comparisons,
            shifts=shifts,
            operations=comparisons + shifts,
            elapsed_time_ms=execution_time_ms,
            complexity_metric={
                "formula": "O(N / M) ~ O(N * M)",
                "progress_pct": 100.0,
                "stage": "전체 텍스트 스캔 완료",
            },
        )
    )

    return {
        "algorithm": "bm_bad_character",
        "name_ko": "보이어-무어 : 나쁜 문자표 (Bad Character)",
        "complexity": "O(N / M) ~ O(N * M)",
        "text": text,
        "pattern": pattern,
        "matches": found_matches,
        "comparisons": comparisons,
        "shifts": shifts,
        "operations": comparisons + shifts,
        "execution_time_ms": execution_time_ms,
        "total_steps": step,
        "history": history,
        "bad_char_table": bc_table,
    }


def run_boyer_moore_good_suffix(text: str, pattern: str) -> Dict[str, Any]:
    """
    착한 접미부 이동법 (Good Suffix Rule & Full Boyer-Moore)
    - 나쁜 문자 이동(bc_shift)과 착한 접미부 이동(gs_shift)을 동시 계산
    - shift = max(bc_shift, gs_shift)를 선택하여 최대 점프 수행
    """
    n, m = len(text), len(pattern)
    history: List[Dict[str, Any]] = []
    comparisons = 0
    shifts = 0
    step = 0
    found_matches: List[int] = []

    start_time = time.perf_counter()

    def get_elapsed() -> float:
        return round((time.perf_counter() - start_time) * 1000, 3)

    if n == 0 or m == 0 or m > n:
        return {
            "algorithm": "bm_good_suffix",
            "name_ko": "보이어-무어 : 착한 접미부 + 복합 (Good Suffix)",
            "text": text,
            "pattern": pattern,
            "matches": [],
            "comparisons": 0,
            "shifts": 0,
            "operations": 0,
            "execution_time_ms": 0.0,
            "history": [],
            "bad_char_table": {},
        }

    bc_table = build_bad_character_table(pattern)

    # 초기 상태 스냅샷
    history.append(
        create_snapshot(
            step=step,
            text=text,
            pattern=pattern,
            text_offset=0,
            pattern_idx=m - 1,
            phase="init",
            phase_name="탐색 대기 (Ready)",
            description=f"[착한 접미부 복합 탐색 시작] 텍스트 길이 {n}, 패턴 길이 {m}",
            active_indices=[m - 1],
            comparisons=0,
            shifts=0,
            operations=0,
            elapsed_time_ms=0.0,
            complexity_metric={
                "formula": "O(N / M) 최선 / O(3N) 선형 보장",
                "progress_pct": 0.0,
                "stage": "나쁜문자표 및 착한접미부 전처리 완료",
            },
            extra={"bad_char_table": bc_table},
        )
    )

    i = 0
    while i <= n - m:
        j = m - 1
        current_matched: List[int] = []

        while j >= 0:
            comparisons += 1
            step += 1
            text_pos = i + j
            active = [text_pos]

            if pattern[j] == text[text_pos]:
                current_matched.append(text_pos)
                progress = min(99.0, round(((i + (m - 1 - j)) / n) * 100, 1))

                history.append(
                    create_snapshot(
                        step=step,
                        text=text,
                        pattern=pattern,
                        text_offset=i,
                        pattern_idx=j,
                        phase="match_char",
                        phase_name="접미부 일치 (Match)",
                        description=f"접미부 일치: Text[{text_pos}]('{text[text_pos]}') == Pattern[{j}]('{pattern[j]}')",
                        active_indices=active,
                        matched_indices=copy.copy(current_matched),
                        found_indices=copy.copy(found_matches),
                        comparisons=comparisons,
                        shifts=shifts,
                        operations=comparisons + shifts,
                        elapsed_time_ms=get_elapsed(),
                        complexity_metric={
                            "formula": "O(N / M) 최선 / O(3N) 선형 보장",
                            "progress_pct": progress,
                            "stage": f"착한 접미부(길이 {len(current_matched)}) 일치 중",
                        },
                    )
                )
                j -= 1
            else:
                mismatched_char = text[text_pos]
                last_pos = bc_table.get(mismatched_char, -1)
                bc_shift = max(1, j - last_pos)
                gs_shift = compute_good_suffix_shift(pattern, j)
                shift = max(bc_shift, gs_shift)

                winner_rule = (
                    "착한 접미부(Good Suffix)"
                    if gs_shift >= bc_shift and gs_shift > 0
                    else "나쁜 문자(Bad Char)"
                )

                step += 1
                progress = min(99.0, round((i / max(1, n - m)) * 100, 1))

                desc = (
                    f"불일치! [나쁜문자={bc_shift}칸, 착한접미부={gs_shift}칸] "
                    f"-> 최적 {shift}칸 이동 선택 ({winner_rule})"
                )

                history.append(
                    create_snapshot(
                        step=step,
                        text=text,
                        pattern=pattern,
                        text_offset=i,
                        pattern_idx=j,
                        phase="mismatch",
                        phase_name=f"{winner_rule} 이동",
                        description=desc,
                        active_indices=[text_pos],
                        matched_indices=copy.copy(current_matched),
                        found_indices=copy.copy(found_matches),
                        comparisons=comparisons,
                        shifts=shifts,
                        operations=comparisons + shifts,
                        shift_amount=shift,
                        elapsed_time_ms=get_elapsed(),
                        complexity_metric={
                            "formula": "O(N / M) 최선 / O(3N) 선형 보장",
                            "progress_pct": progress,
                            "stage": f"max(BC:{bc_shift}, GS:{gs_shift}) = {shift}칸 도약",
                        },
                        extra={
                            "bc_shift": bc_shift,
                            "gs_shift": gs_shift,
                            "winner_rule": winner_rule,
                        },
                    )
                )

                i += shift
                shifts += 1
                break

        if j < 0:
            found_matches.append(i)
            step += 1
            progress = min(100.0, round(((i + m) / n) * 100, 1))

            # 전체 일치 시 접두부 일치 길이 기반 이동
            shift = 1
            for length in range(m - 1, 0, -1):
                if pattern.startswith(pattern[m - length :]):
                    shift = m - length
                    break

            history.append(
                create_snapshot(
                    step=step,
                    text=text,
                    pattern=pattern,
                    text_offset=i,
                    pattern_idx=0,
                    phase="found",
                    phase_name="패턴 발견 (Found!)",
                    description=f"🎉 패턴 발견! 인덱스 [{i} ~ {i + m - 1}] 구간 일치 ({shift}칸 도약)",
                    active_indices=list(range(i, i + m)),
                    matched_indices=list(range(i, i + m)),
                    found_indices=copy.copy(found_matches),
                    comparisons=comparisons,
                    shifts=shifts,
                    operations=comparisons + shifts,
                    shift_amount=shift,
                    elapsed_time_ms=get_elapsed(),
                    complexity_metric={
                        "formula": "O(N / M) 최선 / O(3N) 선형 보장",
                        "progress_pct": progress,
                        "stage": f"일치 인덱스 {i} 등록 후 접두부 기준 {shift}칸 이동",
                    },
                )
            )
            i += shift
            shifts += 1

    end_time = time.perf_counter()
    execution_time_ms = round((end_time - start_time) * 1000, 3)

    # 최종 완료
    step += 1
    history.append(
        create_snapshot(
            step=step,
            text=text,
            pattern=pattern,
            text_offset=n,
            pattern_idx=-1,
            phase="completed",
            phase_name="탐색 완료 (Completed)",
            description=f"착한 접미부 복합 탐색 완료! 총 {len(found_matches)}개 매칭 (비교 {comparisons}회, 이동 {shifts}회)",
            found_indices=copy.copy(found_matches),
            comparisons=comparisons,
            shifts=shifts,
            operations=comparisons + shifts,
            elapsed_time_ms=execution_time_ms,
            complexity_metric={
                "formula": "O(N / M) 최선 / O(3N) 선형 보장",
                "progress_pct": 100.0,
                "stage": "전체 텍스트 스캔 완료",
            },
        )
    )

    return {
        "algorithm": "bm_good_suffix",
        "name_ko": "보이어-무어 : 착한 접미부 + 복합 (Good Suffix)",
        "complexity": "O(N / M) 최선 / O(3N) 최악",
        "text": text,
        "pattern": pattern,
        "matches": found_matches,
        "comparisons": comparisons,
        "shifts": shifts,
        "operations": comparisons + shifts,
        "execution_time_ms": execution_time_ms,
        "total_steps": step,
        "history": history,
        "bad_char_table": bc_table,
    }


def compare_boyer_moore(
    text: Optional[str] = None, pattern: Optional[str] = None
) -> Dict[str, Any]:
    """나쁜 문자표와 착한 접미부 규칙을 적용한 보이어-무어 동시 실행 및 성능 비교 지표 반환"""
    default_text = "GCATGCGTAGGTAGCGTAGAG"
    default_pattern = "GCGTAG"

    t = (text or default_text).strip()
    p = (pattern or default_pattern).strip()

    bc_res = run_boyer_moore_bad_char(t, p)
    gs_res = run_boyer_moore_good_suffix(t, p)

    saved_comps = bc_res["comparisons"] - gs_res["comparisons"]
    efficiency_pct = (
        round((saved_comps / max(1, bc_res["comparisons"])) * 100, 1)
        if bc_res["comparisons"] > 0
        else 0.0
    )

    return {
        "status": "success",
        "text": t,
        "pattern": p,
        "text_length": len(t),
        "pattern_length": len(p),
        "bad_character": bc_res,
        "good_suffix": gs_res,
        "benchmark": {
            "bc_comparisons": bc_res["comparisons"],
            "gs_comparisons": gs_res["comparisons"],
            "saved_comparisons": saved_comps,
            "efficiency_gain_pct": efficiency_pct,
            "bc_shifts": bc_res["shifts"],
            "gs_shifts": gs_res["shifts"],
            "bc_time_ms": bc_res["execution_time_ms"],
            "gs_time_ms": gs_res["execution_time_ms"],
            "matches_found": gs_res["matches"],
            "matches_count": len(gs_res["matches"]),
            "winner_efficiency": "good_suffix"
            if gs_res["comparisons"] <= bc_res["comparisons"]
            else "bad_character",
        },
    }

