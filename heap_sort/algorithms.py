"""
Heap Sort vs Counting Sort Engine with Step-by-Step Snapshot Generation
Stitch Project: projects/9894791412803030970 (Dual Sort Visualizer Dashboard)

비교 분석:
1. 힙 정렬 (Heap Sort):
   - 시간 복잡도: O(N log N) (최선, 평균, 최악 동일)
   - 공간 복잡도: O(1) 제자리 정렬(In-place)
   - 특성: 비교 기반(Comparison-based), 불안정 정렬(Unstable)
2. 도수 정렬 (Counting Sort):
   - 시간 복잡도: O(N + K) (K: 데이터 최댓값 범위)
   - 공간 복잡도: O(K) 추가 보조 배열 필요
   - 특성: 비비교 기반(Non-comparison), 안정 정렬(Stable)
"""

import copy
import math
import time
import random
from typing import List, Dict, Any, Optional


def create_snapshot(
    step: int,
    array: List[int],
    description: str,
    phase: str,
    phase_name: str,
    active_indices: Optional[List[int]] = None,
    secondary_indices: Optional[List[int]] = None,
    sorted_indices: Optional[List[int]] = None,
    comparisons: int = 0,
    swaps: int = 0,
    operations: int = 0,
    elapsed_time_ms: float = 0.0,
    complexity_metric: Optional[Dict[str, Any]] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """공통 스냅샷 딕셔너리 생성 헬퍼 (히스토그램 막대 데이터 및 메타데이터 포함)"""
    snapshot = {
        "step": step,
        "array": copy.deepcopy(array),
        "description": description,
        "phase": phase,
        "phase_name": phase_name,
        "active_indices": active_indices or [],
        "secondary_indices": secondary_indices or [],
        "sorted_indices": sorted_indices or [],
        "comparisons": comparisons,
        "swaps": swaps,
        "operations": operations,
        "elapsed_time_ms": elapsed_time_ms,
        "time_complexity": complexity_metric or {},
    }
    if extra:
        snapshot.update(extra)
    return snapshot


def run_heap_sort(initial_array: List[int]) -> Dict[str, Any]:
    """
    힙 정렬 (Heap Sort)
    - 최대 힙(Max Heap) 구축 과정 추적
    - 루트 최대값과 말단 요소 교환(Swap) 및 정렬 완료 배열 확장 추적
    - 단계별 비교(comparisons), 교환(swaps), 연산(operations) 및 O(N log N) 진행 상태 기록
    """
    arr = copy.deepcopy(initial_array)
    n = len(arr)
    history: List[Dict[str, Any]] = []
    comparisons = 0
    swaps = 0
    step = 0
    sorted_indices: List[int] = []

    start_time = time.perf_counter()

    def get_elapsed() -> float:
        return round((time.perf_counter() - start_time) * 1000, 3)

    # 이론적 추정 단계 수 (N log2 N * 2.2)
    estimated_total_steps = max(10, int(n * math.log2(max(2, n)) * 2.2))

    def calc_complexity_progress(current_step: int, stage_name: str) -> Dict[str, Any]:
        pct = min(99.5, round((current_step / max(1, estimated_total_steps)) * 100, 1))
        return {
            "formula": "O(N log N)",
            "progress_pct": pct,
            "stage": stage_name,
            "theoretical_bound": f"N={n}, N*log(N)≈{int(n * math.log2(max(2, n)))}",
        }

    # 초기 상태 스냅샷
    history.append(
        create_snapshot(
            step=step,
            array=arr,
            description="[힙 정렬 시작] 원본 배열 초기 상태입니다.",
            phase="init",
            phase_name="대기 중 (Ready)",
            sorted_indices=[],
            comparisons=0,
            swaps=0,
            operations=0,
            elapsed_time_ms=0.0,
            complexity_metric=calc_complexity_progress(0, "초기화"),
        )
    )

    if n <= 1:
        end_time = time.perf_counter()
        return {
            "algorithm": "heap_sort",
            "name_ko": "힙 정렬 (Heap Sort)",
            "complexity": "O(N log N)",
            "in_place": True,
            "is_stable": False,
            "original_array": initial_array,
            "sorted_array": arr,
            "comparisons": 0,
            "swaps": 0,
            "operations": 0,
            "execution_time_ms": round((end_time - start_time) * 1000, 3),
            "total_steps": 1,
            "history": history,
        }

    def heapify(length: int, root_idx: int):
        nonlocal step, comparisons, swaps
        largest = root_idx
        left = 2 * root_idx + 1
        right = 2 * root_idx + 2

        active = [root_idx]
        comparisons += 1
        if left < length:
            comparisons += 1
            active.append(left)
            if arr[left] > arr[largest]:
                largest = left

        if right < length:
            comparisons += 1
            active.append(right)
            if arr[right] > arr[largest]:
                largest = right

        step += 1
        history.append(
            create_snapshot(
                step=step,
                array=arr,
                description=f"부모 노드 [{root_idx}]와 자식 노드 비교 탐색",
                phase="heapify_compare",
                phase_name="1단계: Heapify 비교 탐색",
                active_indices=active,
                sorted_indices=copy.copy(sorted_indices),
                comparisons=comparisons,
                swaps=swaps,
                operations=comparisons + swaps,
                elapsed_time_ms=get_elapsed(),
                complexity_metric=calc_complexity_progress(step, "Heapify 트리 탐색"),
            )
        )

        if largest != root_idx:
            swaps += 1
            step += 1
            arr[root_idx], arr[largest] = arr[largest], arr[root_idx]
            history.append(
                create_snapshot(
                    step=step,
                    array=arr,
                    description=f"최대 힙 조건 유지를 위해 인덱스 [{root_idx}] <-> [{largest}] 교환(Swap)",
                    phase="heapify_swap",
                    phase_name="1단계: 힙 구조화 교환",
                    active_indices=[root_idx, largest],
                    sorted_indices=copy.copy(sorted_indices),
                    comparisons=comparisons,
                    swaps=swaps,
                    operations=comparisons + swaps,
                    elapsed_time_ms=get_elapsed(),
                    complexity_metric=calc_complexity_progress(step, "노드 교환 및 재귀 전파"),
                )
            )
            heapify(length, largest)

    # 1. Build Max-Heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)

    step += 1
    history.append(
        create_snapshot(
            step=step,
            array=arr,
            description="[1단계 완료] 초기 배열을 최대 힙(Max-Heap) 구조로 변환 완료",
            phase="heap_built",
            phase_name="1단계 완료: 최대 힙 생성",
            sorted_indices=[],
            comparisons=comparisons,
            swaps=swaps,
            operations=comparisons + swaps,
            elapsed_time_ms=get_elapsed(),
            complexity_metric=calc_complexity_progress(step, "최대 힙 구성 완료"),
        )
    )

    # 2. Extract Elements
    for i in range(n - 1, 0, -1):
        swaps += 1
        step += 1
        arr[0], arr[i] = arr[i], arr[0]
        sorted_indices.append(i)
        history.append(
            create_snapshot(
                step=step,
                array=arr,
                description=f"루트 최대값 {arr[i]}을 정렬 위치 [{i}]로 이동 및 교환",
                phase="extract_root",
                phase_name="2단계: 정렬 추출 (Extract)",
                active_indices=[0, i],
                sorted_indices=copy.copy(sorted_indices),
                comparisons=comparisons,
                swaps=swaps,
                operations=comparisons + swaps,
                elapsed_time_ms=get_elapsed(),
                complexity_metric=calc_complexity_progress(step, f"루트 추출 (남은 크기: {i})"),
            )
        )
        heapify(i, 0)

    if n > 0:
        sorted_indices.append(0)

    end_time = time.perf_counter()
    execution_time_ms = round((end_time - start_time) * 1000, 3)

    # 최종 완료 스냅샷
    step += 1
    final_metric = {
        "formula": "O(N log N)",
        "progress_pct": 100.0,
        "stage": "정렬 완료 (Sorted)",
        "theoretical_bound": f"N={n}, N*log(N)≈{int(n * math.log2(max(2, n)))}",
    }
    history.append(
        create_snapshot(
            step=step,
            array=arr,
            description=f"[힙 정렬 완료] 총 {len(arr)}개 요소 O(N log N) 정렬 완료",
            phase="completed",
            phase_name="정렬 완료 (Sorted)",
            sorted_indices=list(range(n)),
            comparisons=comparisons,
            swaps=swaps,
            operations=comparisons + swaps,
            elapsed_time_ms=execution_time_ms,
            complexity_metric=final_metric,
        )
    )

    total_ops = comparisons + swaps

    return {
        "algorithm": "heap_sort",
        "name_ko": "힙 정렬 (Heap Sort)",
        "complexity": "O(N log N)",
        "in_place": True,
        "is_stable": False,
        "original_array": initial_array,
        "sorted_array": arr,
        "comparisons": comparisons,
        "swaps": swaps,
        "operations": total_ops,
        "execution_time_ms": execution_time_ms,
        "total_steps": step,
        "history": history,
    }


def run_counting_sort(initial_array: List[int]) -> Dict[str, Any]:
    """
    도수 정렬 (Counting Sort)
    - 1단계: 각 데이터 발생 빈도 계수 (Count 배열) (O(N))
    - 2단계: 도수 누적합 계산 (Prefix Sum) (O(K))
    - 3단계: 원본 역순 주사를 통한 안정 출력 배열(Output) 배치 (O(N))
    - 4단계: 최종 원본 복원 및 O(N + K) 진행률 기록
    """
    arr = copy.deepcopy(initial_array)
    n = len(arr)
    history: List[Dict[str, Any]] = []
    step = 0
    operations = 0

    start_time = time.perf_counter()

    def get_elapsed() -> float:
        return round((time.perf_counter() - start_time) * 1000, 3)

    if n == 0:
        return {
            "algorithm": "counting_sort",
            "name_ko": "도수 정렬 (Counting Sort)",
            "complexity": "O(N + K)",
            "in_place": False,
            "is_stable": True,
            "original_array": initial_array,
            "sorted_array": [],
            "comparisons": 0,
            "swaps": 0,
            "operations": 0,
            "execution_time_ms": 0.0,
            "total_steps": 0,
            "history": [],
        }

    max_val = max(arr)
    min_val = min(min(arr), 0)
    range_k = max_val - min_val + 1
    total_theoretical_steps = n + range_k + n

    def calc_complexity_progress(current_step_count: int, stage_name: str) -> Dict[str, Any]:
        pct = min(99.5, round((current_step_count / max(1, total_theoretical_steps)) * 100, 1))
        return {
            "formula": f"O(N + K) (K={range_k})",
            "progress_pct": pct,
            "stage": stage_name,
            "theoretical_bound": f"N={n}, K={range_k}, N+K={n + range_k}",
        }

    # 초기 상태
    history.append(
        create_snapshot(
            step=step,
            array=arr,
            description="[도수 정렬 시작] 원본 배열 초기 상태입니다.",
            phase="init",
            phase_name="대기 중 (Ready)",
            sorted_indices=[],
            comparisons=0,
            swaps=0,
            operations=0,
            elapsed_time_ms=0.0,
            complexity_metric=calc_complexity_progress(0, "초기화"),
        )
    )

    counts = [0] * range_k
    step_tracker = 0

    # Phase 1: Frequency count (O(N))
    for i in range(n):
        val = arr[i]
        counts[val - min_val] += 1
        operations += 1
        step += 1
        step_tracker += 1
        history.append(
            create_snapshot(
                step=step,
                array=arr,
                description=f"도수 계수: 원본 index[{i}]의 값 {val} 빈도 누적 ({counts[val - min_val]}회)",
                phase="frequency_counting",
                phase_name="1단계: 빈도수 집계 (O(N))",
                active_indices=[i],
                comparisons=0,
                swaps=0,
                operations=operations,
                elapsed_time_ms=get_elapsed(),
                complexity_metric=calc_complexity_progress(step_tracker, "도수 배열 Count[] 빈도 카운팅"),
                extra={"current_val": val, "frequency": counts[val - min_val]},
            )
        )

    # Phase 2: Cumulative Sum (Prefix Sum) (O(K))
    for i in range(1, range_k):
        counts[i] += counts[i - 1]
        operations += 1
        step_tracker += 1

    step += 1
    history.append(
        create_snapshot(
            step=step,
            array=arr,
            description=f"도수 누적합(Prefix Sum) 계산 완료 (최댓값 범위 K={range_k})",
            phase="prefix_sum_computed",
            phase_name="2단계: 누적합 계산 (O(K))",
            comparisons=0,
            swaps=0,
            operations=operations,
            elapsed_time_ms=get_elapsed(),
            complexity_metric=calc_complexity_progress(step_tracker, "도수 누적합(Prefix Sum) 인덱스 매핑"),
            extra={"range_k": range_k},
        )
    )

    # Phase 3: Placement into Output array (O(N))
    output = copy.copy(arr)
    working_counts = copy.copy(counts)
    sorted_pos: List[int] = []

    for i in range(n - 1, -1, -1):
        val = arr[i]
        target_idx = working_counts[val - min_val] - 1
        working_counts[val - min_val] -= 1
        output[target_idx] = val
        sorted_pos.append(target_idx)
        operations += 2
        step += 1
        step_tracker += 1

        history.append(
            create_snapshot(
                step=step,
                array=copy.copy(output),
                description=f"출력 배열 안정 배치: 값 {val} -> 위치 index[{target_idx}]",
                phase="output_placement",
                phase_name="3단계: 결과 배열 재배치 (O(N))",
                active_indices=[target_idx],
                secondary_indices=[i],
                sorted_indices=copy.copy(sorted_pos),
                comparisons=0,
                swaps=0,
                operations=operations,
                elapsed_time_ms=get_elapsed(),
                complexity_metric=calc_complexity_progress(step_tracker, "출력 배열 역순 안정 배치"),
            )
        )

    end_time = time.perf_counter()
    execution_time_ms = round((end_time - start_time) * 1000, 3)

    # 최종 완료
    step += 1
    final_metric = {
        "formula": f"O(N + K) (K={range_k})",
        "progress_pct": 100.0,
        "stage": "정렬 완료 (Sorted)",
        "theoretical_bound": f"N={n}, K={range_k}, N+K={n + range_k}",
    }
    history.append(
        create_snapshot(
            step=step,
            array=output,
            description=f"[도수 정렬 완료] O(N + K) 선형 연산으로 {n}개 정렬 완료 (비교 0회)",
            phase="completed",
            phase_name="정렬 완료 (Sorted)",
            sorted_indices=list(range(n)),
            comparisons=0,
            swaps=0,
            operations=operations,
            elapsed_time_ms=execution_time_ms,
            complexity_metric=final_metric,
        )
    )

    return {
        "algorithm": "counting_sort",
        "name_ko": "도수 정렬 (Counting Sort)",
        "complexity": f"O(N + K) (K={range_k})",
        "in_place": False,
        "is_stable": True,
        "original_array": initial_array,
        "sorted_array": output,
        "comparisons": 0,
        "swaps": 0,
        "operations": operations,
        "execution_time_ms": execution_time_ms,
        "total_steps": step,
        "history": history,
    }


def compare_heap_and_counting(
    initial_array: Optional[List[int]] = None, size: int = 50
) -> Dict[str, Any]:
    """두 정렬 알고리즘 동시 실행 및 단계별 히스토그램 스냅샷 + 성능 벤치마크 지표 반환"""
    if initial_array is None or len(initial_array) == 0:
        arr = [random.randint(8, 100) for _ in range(size)]
    else:
        arr = copy.deepcopy(initial_array)

    heap_res = run_heap_sort(arr)
    count_res = run_counting_sort(arr)

    ops_ratio = (
        round(heap_res["operations"] / max(1, count_res["operations"]), 2)
        if count_res["operations"] > 0
        else 1.0
    )

    return {
        "status": "success",
        "array_size": len(arr),
        "dataset_summary": {
            "size": len(arr),
            "min": min(arr) if arr else 0,
            "max": max(arr) if arr else 0,
            "sample_head": arr[:10],
        },
        "heap_sort": heap_res,
        "counting_sort": count_res,
        "benchmark": {
            "heap_ops": heap_res["operations"],
            "count_ops": count_res["operations"],
            "ops_ratio_heap_to_count": ops_ratio,
            "heap_time_ms": heap_res["execution_time_ms"],
            "count_time_ms": count_res["execution_time_ms"],
            "winner_speed": "counting_sort"
            if count_res["execution_time_ms"] <= heap_res["execution_time_ms"]
            else "heap_sort",
            "winner_memory": "heap_sort",
        },
    }
