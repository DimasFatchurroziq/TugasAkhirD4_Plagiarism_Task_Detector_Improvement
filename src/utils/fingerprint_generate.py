def fingerprint_generate(window_list):
    fingerprint_list = []

    window_length = len(window_list[0])
    window_length_min_1 = window_length - 1

    for i in range(len(window_list)):

        if i > 0:
            # cek jarak index
            if (window_list[i][window_length_min_1][0] - fingerprint_list[index_list][0]) < window_length:
                smallest_hash = fingerprint_list[index_list]

                # bandingkan dengan elemen terakhir window
                last_element = window_list[i][window_length_min_1]
                if (
                    last_element[1] < smallest_hash[1] or
                    (last_element[1] == smallest_hash[1] and last_element[0] > smallest_hash[0])
                ):
                    smallest_hash = last_element
                    fingerprint_list.append(smallest_hash)
                    index_list += 1

            else:
                smallest_hash = window_list[i][0]
                for x in range(1, window_length):
                    if (
                        window_list[i][x][1] < smallest_hash[1] or
                        (window_list[i][x][1] == smallest_hash[1] and
                         window_list[i][x][0] > smallest_hash[0])
                    ):
                        smallest_hash = window_list[i][x]

                fingerprint_list.append(smallest_hash)
                index_list += 1

        else:
            smallest_hash = window_list[i][0]
            for x in range(1, window_length):
                if (
                    window_list[i][x][1] < smallest_hash[1] or
                    (window_list[i][x][1] == smallest_hash[1] and
                     window_list[i][x][0] > smallest_hash[0])
                ):
                    smallest_hash = window_list[i][x]

            fingerprint_list.append(smallest_hash)
            index_list = 0

    return fingerprint_list

if __name__ == "__main__":
   
    window_list = [
        [[0, 4000], [1, 3500], [2, 3600], [3, 3400], [4, 3800]],
        [[1, 3500], [2, 3600], [3, 3400], [4, 3800], [5, 3300]],
        [[2, 3600], [3, 3400], [4, 3800], [5, 3300], [6, 3700]],
    ]
    hasil = fingerprint_generate(window_list)
    print(hasil)