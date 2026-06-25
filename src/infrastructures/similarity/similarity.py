def jaccard_similarity(intersection, length_1, length_2):
    union = length_1 + length_2 - intersection
    if union == 0:
        return 0.0
    similarity = intersection / union
    # print(intersection, length_1, length_2, union)
    return similarity

def containment_similarity(intersection, min_length):
    if min_length == 0:
        return 0.0
    similarity = intersection / min_length
    # print(intersection, min_length)
    return similarity