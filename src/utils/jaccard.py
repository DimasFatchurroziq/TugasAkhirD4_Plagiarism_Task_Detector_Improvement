def jaccard_similarity(intersection, length_1, length_2):
    union = length_1 + length_2 - intersection
    similarity = intersection / union
    return similarity