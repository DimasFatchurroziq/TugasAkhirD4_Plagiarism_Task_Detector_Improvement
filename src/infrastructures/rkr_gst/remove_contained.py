def remove_contained(tiles_list):
    intervals = []

    for i in range(len(tiles_list)):
        start_i = tiles_list[i][1]
        end_i = tiles_list[i][1] + tiles_list[i][2] - 1
        contained = False

        for j in range(len(tiles_list)):
            if i == j:
                continue

            start_j = tiles_list[j][1]
            end_j = tiles_list[j][1] + tiles_list[j][2] - 1

            if start_i >= start_j and end_i <= end_j:
                contained = True
                break

        if not contained:
            intervals.append(tiles_list[i][2])

    return intervals

if __name__ == "__main__":
    # asu = [[0, 17], [38, 47], [52, 753], [425, 440], [287, 302], [678, 727], [425, 440], [1333, 1338], [756, 2039]]
    asu = [[0, 0, 18], [42, 38, 10], [56, 52, 702], [760, 425, 16], [778, 287, 16], [814, 678, 50], [866, 425, 16], [882, 1333, 6], [890, 756, 1284]]
    kaki = remove_contained(asu)
    print(kaki)