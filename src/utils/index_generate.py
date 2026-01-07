def generate_index(list):
    indexing_list = []
    for i in range(len(list)):
        indexing_list.append([i, list[i]])
    return indexing_list