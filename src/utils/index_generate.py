def generate_index(list):
    indexing_list = []
    for i in range(len(list)):
        indexing_list.append([list[i], i])
    return indexing_list