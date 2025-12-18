def fingerprint(window_list):
    fingerprint_list = []
    for i in window_list:
        terkecil = i[0]
        fingerprint_list.extend
    
    # [index, hash]

    for i in range(len(window_list)) :
        if (i == 1) :
            terkecil = window_list[i][0][1]
            for x in range(0, 3) :
                if (window_list[i][x][1] < terkecil) :
                    terkecil = window_list[i][x][1]
        elif ( i > 1) :
            terkecil = fingerprint_list[i-1][0][1]
            
                    
        fingerprint_list.extend()