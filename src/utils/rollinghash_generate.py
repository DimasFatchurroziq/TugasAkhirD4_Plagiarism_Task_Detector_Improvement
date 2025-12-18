def rollinghash_text(ngrams_list):
    base = 4
    hash_list = []
    for text in ngrams_list:
        hash_value = 0
        for word in text:
            for char in word:
                hash_value = (hash_value * base + ord(char))
        hash_list.append(hash_value) 
    return hash_list 

if __name__ == '__main__':
    ko=rollinghash_text([['I', 'n', 'd'], ['n', 'd', 'o'], ['d', 'o', 'n'], ['o', 'n', 'e'], ['n', 'e', 's'], ['e', 's', 'h'], ['s', 'h', ' '], ['h', ' ', '.']])
    print(ko)