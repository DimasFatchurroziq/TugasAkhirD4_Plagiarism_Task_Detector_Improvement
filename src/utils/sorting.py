def timsort(fingerprint_list, n):
    sort_fingerprint = sorted(fingerprint_list, key=lambda x: x[n])
    return sort_fingerprint

# if __name__ == "__main__":
#     kk = [[0, 2266], [1, 2332], [2, 2340], [5, 2320], [7, 2290], [8, 2098], [11, 2095]]
#     asi = timsort(kk)
#     print(asi)