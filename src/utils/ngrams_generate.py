def generate_ngrams(tokens_list, n):
    ngrams_list = []
    for i in range(len(tokens_list) - n + 1):
        ngrams_list.append(tokens_list[i:i + n])
    return ngrams_list

if __name__ == "__main__":
    teks = [[1708, 0], [2271, 1], [2154, 2], [2317, 3], [2279, 4], [2180, 5], [2288, 6], [1838, 7]]
    babi = generate_ngrams(teks, 4)
    print(babi)
    print(len(teks))
    for i in range(len(teks)):
        print(i)