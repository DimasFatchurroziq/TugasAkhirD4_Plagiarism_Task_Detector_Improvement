import bisect

def binary_search(sorted_list, target, index):
    keys = [x[index] for x in sorted_list]
    
    idx_start = bisect.bisect_left(keys, target[index])
    idx_end = bisect.bisect_right(keys, target[index])

    matched = sorted_list[idx_start:idx_end]
    for item in matched:
        return([target[1-index]] + item)



