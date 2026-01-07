def fingerprint_generate(window_list):
    fingerprint_list = []

    for i in range(len(window_list)) :

        if (i > 0) :
            if (window_list[i][3][0] - fingerprint_list[index_list][0] < 4):

                smallest_hash = fingerprint_list[index_list] 
                
                if (window_list[i][3][1] <= smallest_hash[1]) :
                    smallest_hash = window_list[i][3]
                    fingerprint_list.append(smallest_hash)
                    index_list += 1
                
            else: #>=4
                smallest_hash = window_list[i][0]
                for x in range(1, 3) :
                    if (window_list[i][x][1] < smallest_hash[1]) :
                        smallest_hash = window_list[i][x]
                fingerprint_list.append(smallest_hash)
                index_list += 1


        else :
            smallest_hash = window_list[i][0]
            for x in range(1, 3) :
                if (window_list[i][x][1] < smallest_hash[1]) :
                    smallest_hash = window_list[i][x]
            fingerprint_list.append(smallest_hash) 

            index_list = 0  

    return fingerprint_list