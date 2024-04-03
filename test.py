def binary_search(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        # 중간값이 타겟과 같으면 인덱스 반환
        if arr[mid] == target:
            return mid
        # 중간값이 타겟보다 작으면 오른쪽 반 탐색
        elif arr[mid] < target:
            left = mid + 1
        # 중간값이 타겟보다 크면 왼쪽 반 탐색
        else:
            right = mid - 1

    # 타겟을 찾지 못한 경우 -1 반환
    return -1

# 정렬된 리스트
arr = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
target = 11

# 이진 탐색 실행
result = binary_search(arr, target)

# 결과 출력
if result != -1:
    print(f"{target}는 리스트에서 {result}번째에 위치해 있습니다.")
else:
    print(f"{target}는 리스트에 존재하지 않습니다.")
