def jaccard_similarity(intersection, length_1, length_2):
    union = length_1 + length_2 - intersection
    similarity = intersection / union
    # print(intersection, length_1, length_2, union)
    return similarity

def containment_similarity(intersection, min_length):
    similarity = intersection / min_length
    # print(intersection, min_length)
    return similarity