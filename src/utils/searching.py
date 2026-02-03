import bisect

def binary_search(sorted_list, target, index):
    result = []
    keys = [x[index] for x in sorted_list]
    
    idx_start = bisect.bisect_left(keys, target[index])
    idx_end = bisect.bisect_right(keys, target[index])

    matched = sorted_list[idx_start:idx_end]
    for item in matched:
        result.append([target[1-index]] + item)
    return result


if __name__ == "__main__":
    sorted_list =[[0, 10], [1, 10], [2, 10]]
    target = [[9, 10], [11,11]]
    index = 1

    result = []
    for item in target:
        sapi = binary_search(sorted_list, item, index)
        print(sapi)
        if sapi:
            result.extend(sapi)

    # hasil = binary_search(sorted_list, target, index)
    print(result)




