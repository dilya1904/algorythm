"""
Sorting Algorithms with Snapshot History Generation
- Shell Sort (셸 정렬)
- Quick Sort (퀵 정렬)
- Merge Sort (병합 정렬)

각 알고리즘의 동작 과정을 단계별 스냅샷(Snapshot)으로 캡처하여
클라이언트에서 프레임 단위로 시각화할 수 있도록 지원합니다.
"""

from typing import List, Dict, Any, Optional
import copy


def create_snapshot(
    step: int,
    array: List[int],
    description: str,
    phase: str,
    active_indices: Optional[List[int]] = None,
    secondary_indices: Optional[List[int]] = None,
    sorted_indices: Optional[List[int]] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """공통 스냅샷 딕셔너리 생성 헬퍼"""
    snapshot = {
        "step": step,
        "array": copy.deepcopy(array),
        "description": description,
        "phase": phase,
        "active_indices": active_indices or [],
        "secondary_indices": secondary_indices or [],
        "sorted_indices": sorted_indices or [],
    }
    if extra:
        snapshot.update(extra)
    return snapshot


def run_shell_sort(initial_array: List[int]) -> Dict[str, Any]:
    """
    셸 정렬 (Shell Sort)
    - 간격(Gap) 크기 변화 기록
    - Gap 단위 그룹화 및 비교 상태 기록
    - 삽입/교환 과정 기록
    """
    arr = copy.deepcopy(initial_array)
    n = len(arr)
    history: List[Dict[str, Any]] = []
    comparisons = 0
    swaps = 0
    step = 0

    # 초기 상태 기록
    history.append(
        create_snapshot(
            step=step,
            array=arr,
            description="[셸 정렬 시작] 원본 배열 초기 상태입니다.",
            phase="init",
            extra={"gap": None, "group_indices": []},
        )
    )

    gap = n // 2
    while gap > 0:
        step += 1
        history.append(
            create_snapshot(
                step=step,
                array=arr,
                description=f"[간격 설정] 간격(Gap)을 {gap}으로 축소합니다. gap={gap} 간격으로 묶인 원소들을 부분 정렬합니다.",
                phase="gap_change",
                extra={"gap": gap, "group_indices": []},
            )
        )

        # gap 간격의 각 그룹에 대해 삽입 정렬 수행
        for i in range(gap, n):
            temp = arr[i]
            j = i
            group = list(range(i % gap, n, gap))

            step += 1
            history.append(
                create_snapshot(
                    step=step,
                    array=arr,
                    description=f"[삽입 대상 선택] 인덱스 {i}(값: {temp})를 gap={gap} 그룹 내 정렬된 부분에 삽입하기 위해 탐색합니다.",
                    phase="select_target",
                    active_indices=[i],
                    secondary_indices=group,
                    extra={"gap": gap, "group_indices": group},
                )
            )

            while j >= gap:
                comparisons += 1
                comp_idx = j - gap
                step += 1
                history.append(
                    create_snapshot(
                        step=step,
                        array=arr,
                        description=f"[비교] 인덱스 {comp_idx}(값: {arr[comp_idx]})와 삽입 대상(값: {temp})을 비교합니다.",
                        phase="compare",
                        active_indices=[comp_idx, j],
                        secondary_indices=group,
                        extra={
                            "gap": gap,
                            "group_indices": group,
                            "comparing": [comp_idx, j],
                        },
                    )
                )

                if arr[comp_idx] > temp:
                    arr[j] = arr[comp_idx]
                    swaps += 1
                    step += 1
                    history.append(
                        create_snapshot(
                            step=step,
                            array=arr,
                            description=f"[이동] {arr[comp_idx]} > {temp}이므로 인덱스 {comp_idx}의 원소를 gap({gap})만큼 뒤(인덱스 {j})로 이동합니다.",
                            phase="shift",
                            active_indices=[comp_idx, j],
                            secondary_indices=group,
                            extra={"gap": gap, "group_indices": group},
                        )
                    )
                    j -= gap
                else:
                    break

            arr[j] = temp
            step += 1
            history.append(
                create_snapshot(
                    step=step,
                    array=arr,
                    description=f"[삽입 완료] 대상 값 {temp}을 인덱스 {j}에 최종 삽입했습니다.",
                    phase="insert",
                    active_indices=[j],
                    secondary_indices=group,
                    extra={"gap": gap, "group_indices": group},
                )
            )

        gap //= 2

    # 최종 정렬 완료 상태
    step += 1
    history.append(
        create_snapshot(
            step=step,
            array=arr,
            description="[셸 정렬 완료] 모든 gap 단계가 완료되어 배열이 완전히 정렬되었습니다.",
            phase="sorted",
            sorted_indices=list(range(n)),
            extra={"gap": 0, "group_indices": []},
        )
    )

    return {
        "algorithm": "shell_sort",
        "name": "셸 정렬 (Shell Sort)",
        "total_steps": len(history),
        "comparisons": comparisons,
        "swaps": swaps,
        "history": history,
    }


def run_quick_sort(initial_array: List[int]) -> Dict[str, Any]:
    """
    퀵 정렬 (Quick Sort)
    - 피벗(Pivot) 지정 스냅샷
    - 피벗과 대소 비교 대상 기록
    - 요소 교환 위치 기록
    - 피벗의 최종 정렬 확정(Fixed) 상태 기록
    """
    arr = copy.deepcopy(initial_array)
    n = len(arr)
    history: List[Dict[str, Any]] = []
    comparisons = 0
    swaps = 0
    step = 0
    fixed_pivots: List[int] = []

    history.append(
        create_snapshot(
            step=step,
            array=arr,
            description="[퀵 정렬 시작] 원본 배열 초기 상태입니다.",
            phase="init",
        )
    )

    def partition(low: int, high: int) -> int:
        nonlocal step, comparisons, swaps
        pivot_idx = high
        pivot_val = arr[pivot_idx]

        step += 1
        history.append(
            create_snapshot(
                step=step,
                array=arr,
                description=f"[피벗 지정] 구간 [{low} ~ {high}]에서 피벗으로 인덱스 {pivot_idx}(값: {pivot_val})를 지정합니다.",
                phase="pivot_select",
                active_indices=[pivot_idx],
                secondary_indices=list(range(low, high)),
                sorted_indices=list(fixed_pivots),
                extra={
                    "pivot_index": pivot_idx,
                    "partition_range": [low, high],
                },
            )
        )

        i = low - 1  # 작은 원소들의 경계 인덱스
        for j in range(low, high):
            comparisons += 1
            step += 1
            history.append(
                create_snapshot(
                    step=step,
                    array=arr,
                    description=f"[피벗과 비교] 원소 인덱스 {j}(값: {arr[j]})와 피벗(값: {pivot_val})을 비교합니다.",
                    phase="compare",
                    active_indices=[j],
                    secondary_indices=[pivot_idx],
                    sorted_indices=list(fixed_pivots),
                    extra={
                        "pivot_index": pivot_idx,
                        "comparing": [j, pivot_idx],
                        "partition_range": [low, high],
                    },
                )
            )

            if arr[j] <= pivot_val:
                i += 1
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    swaps += 1
                    step += 1
                    history.append(
                        create_snapshot(
                            step=step,
                            array=arr,
                            description=f"[교환] {arr[j]} <= {pivot_val} 이므로 인덱스 {i}와 {j}의 원소를 맞교환하여 작은 값을 왼쪽으로 모읍니다.",
                            phase="swap",
                            active_indices=[i, j],
                            secondary_indices=[pivot_idx],
                            sorted_indices=list(fixed_pivots),
                            extra={
                                "pivot_index": pivot_idx,
                                "swapped": [i, j],
                                "partition_range": [low, high],
                            },
                        )
                    )

        # 피벗을 올바른 정렬 위치(i + 1)로 이동
        final_pivot_pos = i + 1
        if final_pivot_pos != pivot_idx:
            arr[final_pivot_pos], arr[pivot_idx] = arr[pivot_idx], arr[final_pivot_pos]
            swaps += 1
            step += 1
            history.append(
                create_snapshot(
                    step=step,
                    array=arr,
                    description=f"[피벗 배치] 피벗 {pivot_val}을 최종 분할 위치인 인덱스 {final_pivot_pos}로 이동합니다.",
                    phase="pivot_move",
                    active_indices=[final_pivot_pos, pivot_idx],
                    sorted_indices=list(fixed_pivots),
                    extra={
                        "pivot_index": final_pivot_pos,
                        "partition_range": [low, high],
                    },
                )
            )

        fixed_pivots.append(final_pivot_pos)
        step += 1
        history.append(
            create_snapshot(
                step=step,
                array=arr,
                description=f"[피벗 위치 확정] 인덱스 {final_pivot_pos}(값: {arr[final_pivot_pos]})의 최종 정렬 위치가 확정되었습니다.",
                phase="pivot_fixed",
                active_indices=[final_pivot_pos],
                sorted_indices=list(fixed_pivots),
                extra={
                    "fixed_pivot": final_pivot_pos,
                    "partition_range": [low, high],
                },
            )
        )

        return final_pivot_pos

    def quick_sort_recursive(low: int, high: int):
        if low < high:
            pi = partition(low, high)
            quick_sort_recursive(low, pi - 1)
            quick_sort_recursive(pi + 1, high)
        elif low == high:
            if low not in fixed_pivots:
                fixed_pivots.append(low)

    quick_sort_recursive(0, n - 1)

    step += 1
    history.append(
        create_snapshot(
            step=step,
            array=arr,
            description="[퀵 정렬 완료] 모든 피벗 분할 및 정렬이 완료되었습니다.",
            phase="sorted",
            sorted_indices=list(range(n)),
        )
    )

    return {
        "algorithm": "quick_sort",
        "name": "퀵 정렬 (Quick Sort)",
        "total_steps": len(history),
        "comparisons": comparisons,
        "swaps": swaps,
        "history": history,
    }


def run_merge_sort(initial_array: List[int]) -> Dict[str, Any]:
    """
    병합 정렬 (Merge Sort)
    - 논리적 분할(Divide) 구간 기록
    - 좌/우 부분 배열 병합 시 원소 비교 과정 기록
    - 임시 배열에서 원본 배열로 덮어쓰기(Overwrite) 상태 기록
    """
    arr = copy.deepcopy(initial_array)
    n = len(arr)
    history: List[Dict[str, Any]] = []
    comparisons = 0
    overwrites = 0
    step = 0

    history.append(
        create_snapshot(
            step=step,
            array=arr,
            description="[병합 정렬 시작] 원본 배열 초기 상태입니다.",
            phase="init",
        )
    )

    def merge(left: int, mid: int, right: int):
        nonlocal step, comparisons, overwrites

        left_part = arr[left : mid + 1]
        right_part = arr[mid + 1 : right + 1]

        step += 1
        history.append(
            create_snapshot(
                step=step,
                array=arr,
                description=f"[병합 준비] 구간 [{left}~{mid}]와 [{mid+1}~{right}]를 병합합니다.",
                phase="merge_start",
                active_indices=list(range(left, right + 1)),
                secondary_indices=[mid],
                extra={
                    "split_range": [left, mid, right],
                    "left_sub": [left, mid],
                    "right_sub": [mid + 1, right],
                    "temp_buffer": [],
                },
            )
        )

        i = 0
        j = 0
        temp: List[int] = []

        while i < len(left_part) and j < len(right_part):
            actual_left_idx = left + i
            actual_right_idx = mid + 1 + j
            comparisons += 1

            step += 1
            history.append(
                create_snapshot(
                    step=step,
                    array=arr,
                    description=f"[병합 비교] 좌측 인덱스 {actual_left_idx}(값: {left_part[i]})와 우측 인덱스 {actual_right_idx}(값: {right_part[j]})를 비교합니다.",
                    phase="merge_compare",
                    active_indices=[actual_left_idx, actual_right_idx],
                    secondary_indices=list(range(left, right + 1)),
                    extra={
                        "comparing": [actual_left_idx, actual_right_idx],
                        "temp_buffer": list(temp),
                        "split_range": [left, mid, right],
                    },
                )
            )

            if left_part[i] <= right_part[j]:
                temp.append(left_part[i])
                step += 1
                history.append(
                    create_snapshot(
                        step=step,
                        array=arr,
                        description=f"[임시 버퍼 수집] 더 작거나 같은 좌측 값 {left_part[i]}을 임시 배열에 적재합니다.",
                        phase="temp_collect",
                        active_indices=[actual_left_idx],
                        secondary_indices=list(range(left, right + 1)),
                        extra={
                            "temp_buffer": list(temp),
                            "collected_from": "left",
                            "split_range": [left, mid, right],
                        },
                    )
                )
                i += 1
            else:
                temp.append(right_part[j])
                step += 1
                history.append(
                    create_snapshot(
                        step=step,
                        array=arr,
                        description=f"[임시 버퍼 수집] 더 작은 우측 값 {right_part[j]}을 임시 배열에 적재합니다.",
                        phase="temp_collect",
                        active_indices=[actual_right_idx],
                        secondary_indices=list(range(left, right + 1)),
                        extra={
                            "temp_buffer": list(temp),
                            "collected_from": "right",
                            "split_range": [left, mid, right],
                        },
                    )
                )
                j += 1

        while i < len(left_part):
            temp.append(left_part[i])
            actual_left_idx = left + i
            step += 1
            history.append(
                create_snapshot(
                    step=step,
                    array=arr,
                    description=f"[잔여 수집] 좌측 부분배열의 남은 원소 {left_part[i]}를 임시 배열에 추가합니다.",
                    phase="temp_collect",
                    active_indices=[actual_left_idx],
                    secondary_indices=list(range(left, right + 1)),
                    extra={
                        "temp_buffer": list(temp),
                        "collected_from": "left_remain",
                        "split_range": [left, mid, right],
                    },
                )
            )
            i += 1

        while j < len(right_part):
            temp.append(right_part[j])
            actual_right_idx = mid + 1 + j
            step += 1
            history.append(
                create_snapshot(
                    step=step,
                    array=arr,
                    description=f"[잔여 수집] 우측 부분배열의 남은 원소 {right_part[j]}를 임시 배열에 추가합니다.",
                    phase="temp_collect",
                    active_indices=[actual_right_idx],
                    secondary_indices=list(range(left, right + 1)),
                    extra={
                        "temp_buffer": list(temp),
                        "collected_from": "right_remain",
                        "split_range": [left, mid, right],
                    },
                )
            )
            j += 1

        # 원본 배열로 덮어쓰기 (Overwrite)
        for k in range(len(temp)):
            overwrite_idx = left + k
            arr[overwrite_idx] = temp[k]
            overwrites += 1
            step += 1
            history.append(
                create_snapshot(
                    step=step,
                    array=arr,
                    description=f"[덮어쓰기 Overwrite] 정렬된 임시 배열의 값 {temp[k]}을 원본 배열 인덱스 {overwrite_idx}에 덮어씌웁니다.",
                    phase="overwrite",
                    active_indices=[overwrite_idx],
                    secondary_indices=list(range(left, right + 1)),
                    extra={
                        "overwriting_index": overwrite_idx,
                        "value": temp[k],
                        "temp_buffer": list(temp),
                        "split_range": [left, mid, right],
                    },
                )
            )

    def merge_sort_recursive(left: int, right: int):
        nonlocal step
        if left < right:
            mid = (left + right) // 2

            step += 1
            history.append(
                create_snapshot(
                    step=step,
                    array=arr,
                    description=f"[논리적 분할 Divide] 구간 [{left} ~ {right}]를 중간점 {mid} 기준으로 좌 [{left}~{mid}]와 우 [{mid+1}~{right}]로 분할합니다.",
                    phase="split",
                    active_indices=list(range(left, right + 1)),
                    secondary_indices=[mid],
                    extra={"split_range": [left, mid, right]},
                )
            )

            merge_sort_recursive(left, mid)
            merge_sort_recursive(mid + 1, right)
            merge(left, mid, right)

    merge_sort_recursive(0, n - 1)

    step += 1
    history.append(
        create_snapshot(
            step=step,
            array=arr,
            description="[병합 정렬 완료] 모든 분할 구간의 병합이 완료되어 전체 배열이 정렬되었습니다.",
            phase="sorted",
            sorted_indices=list(range(n)),
        )
    )

    return {
        "algorithm": "merge_sort",
        "name": "병합 정렬 (Merge Sort)",
        "total_steps": len(history),
        "comparisons": comparisons,
        "overwrites": overwrites,
        "history": history,
    }


def compare_all_sorts(initial_array: List[int]) -> Dict[str, Any]:
    """3가지 정렬 알고리즘을 모두 실행하고 종합 스냅샷 번들을 반환"""
    shell_result = run_shell_sort(initial_array)
    quick_result = run_quick_sort(initial_array)
    merge_result = run_merge_sort(initial_array)

    max_steps = max(
        shell_result["total_steps"],
        quick_result["total_steps"],
        merge_result["total_steps"],
    )

    return {
        "initial_array": initial_array,
        "array_length": len(initial_array),
        "max_steps": max_steps,
        "results": {
            "shell_sort": shell_result,
            "quick_sort": quick_result,
            "merge_sort": merge_result,
        },
    }

