def penggabung(list_blocks):
    result = []
    temp = [list_blocks[0]]
    
    for block in list_blocks[1:]:
        if block["type"] == temp[-1]["type"] and block["source"] == "TYPING":
            temp[-1]["content"] = temp[-1]["content"] + block["content"]
        else:
            result.extend(temp)
            temp = [block]

    result.extend(temp)

    return result

def penggabung_v2(extracted):
    if not extracted:
        return []

    result = []
    temp = list(extracted[0])  # ubah tuple → list biar bisa dimodif

    for text, fonts, bidx in extracted[1:]:
        if (
            len(temp[0]) < 60 and
            set(temp[1]) == set(fonts)
        ):
            # gabungkan ke blok terakhir
            temp[0] += text
        else:
            result.append(tuple(temp))
            temp = [text, fonts, bidx]

    result.append(tuple(temp))
    return result

blocks = [
    {
        "content": "Ini adalah contoh teks biasa untuk pengujian aplikasi.",
        "type": "text",
        "source": "typing"
    },
    {
        "content": "print('Hello World')",
        "type": "code",
        "source": "typing"
    },
    {
        "content": "def add(a, b): return a + b",
        "type": "code",
        "source": "image"
    },
    {
        "content": "Paragraf lain dengan isi acak sebagai dummy data.",
        "type": "text",
        "source": "typing"
    },
    {
        "content": "for i in range(5): print(i)",
        "type": "code",
        "source": "image"
    },
    {
        "content": "# hasil ekstraksi kode dari gambar\nx = 10\ny = 20\nprint(x + y)",
        "type": "code",
        "source": "image"
    }
]

if __name__ == "__main__":
    blocks = penggabung(blocks)
    print(blocks)
