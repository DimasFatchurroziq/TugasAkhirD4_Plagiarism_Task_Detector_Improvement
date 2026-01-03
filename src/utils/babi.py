def fingerprint(window_list):
    fingerprint_list = []
    
    # [hash, index]

    # [[[1708, 0], [2271, 1], [2154, 2], [2317, 3]],   [[2271, 1], [2154, 2], [2317, 3], [2279, 4]]], 

    # [[1708, 0], [2271, 3], [2154, 10], [2317, 12]]

    for i in range(len(window_list)) :
        
        if (i == 0) :
            terkecil = window_list[i][0]
            for x in range(1, 3) :
                if (window_list[i][x][0] < terkecil[0]) :
                    terkecil = window_list[i][x]
            fingerprint_list.append(terkecil) 

            index_list = 0  
            print(1, index_list) 

        else :
            if (window_list[i][3][1] - fingerprint_list[index_list][1] < 4):

                terkecil = fingerprint_list[index_list] 
                
                if (window_list[i][3][0] <= terkecil[0]) :
                    terkecil = window_list[i][3]
                    fingerprint_list.append(terkecil)
                    index_list += 1
                
                print(2, index_list)

            else: #>=4
                terkecil = window_list[i][0]
                for x in range(1, 3) :
                    if (window_list[i][x][0] < terkecil[0]) :
                        terkecil = window_list[i][x]
                fingerprint_list.append(terkecil)
                index_list += 1

                print(3, index_list)

    return fingerprint_list


if __name__ == "__main__":
    window_list = [[[1708, 0], [2271, 1], [2154, 2], [2317, 3]], [[2271, 1], [2154, 2], [2317, 3], [2279, 4]], [[2154, 2], [2317, 3], [2279, 4], [2180, 5]], [[2317, 3], [2279, 4], [2180, 5], [2288, 6]], [[2279, 4], [2180, 5], [2288, 6], [1838, 7]]]
    babi = fingerprint(window_list)
    print(babi)

