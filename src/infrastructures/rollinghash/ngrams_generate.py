def generate_ngrams(tokens_list, n):
    ngrams_list = []
    for i in range(len(tokens_list) - n + 1):
        ngrams_list.append(tokens_list[i:i + n])
    return ngrams_list