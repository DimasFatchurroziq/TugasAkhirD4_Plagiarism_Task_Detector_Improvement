texts = ['Bagus! Mari kita breakdown berdasarkan komponen-komponen utama aplikasi backend: ', ' ', '## 1. API Layer (Interface dengan Dunia Luar) ', ' ', '**Design & Architecture** ', '- RESTful API principles (HTTP methods, status codes, resource naming) ', '- GraphQL untuk query flexibility ', '- gRPC untuk high-performance internal services ', '- API versioning strategies (URL, header, content negotiation) ']

def mapping(texts):
    cleaned = []
    mapping = []

    cleaned_append = cleaned.append
    mapping_append = mapping.append

    i = 0  # counter global

    for text in texts:
        for ch in text:
            if ch.isalpha():
                cleaned_append(ch)
                mapping_append(i)
            i += 1

    return cleaned, mapping



def mapping_to_range(mapping_process_list):

    result = []

    start = 0

    for i in range(len(mapping_process_list)):
        length = len(mapping_process_list[i])
        end = start + length - 1

        result.append([start, end])

        start = end + 1