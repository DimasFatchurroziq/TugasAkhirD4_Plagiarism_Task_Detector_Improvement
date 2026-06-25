import re
from dataclasses import dataclass
from typing import Optional

KEYWORDS = {'int', 'float', 'double', 'char', 'void', 'short', 'long', 'printf', 'scanf', 'gets', 'puts', 'include', 'stdio', 'stdlib', 'string', 'math', 'iostream', 'fstream', 'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extern', 'for', 'goto', 'if', 'register', 'return', 'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while'}

TOKEN_SPEC = [
    ('COMMENT',   r'//.*'),
    ('MCOMMENT',  r'/\*[\s\S]*?\*/'),
    ('STRING',    r'"[^"\\]*(\\.[^"\\]*)*"'),
    ('UNTERM_STR',r'"[^"\\]*(\\.[^"\\]*)*'),
    ('FLOAT',     r'\d+\.\d+'),
    ('NUMBER',    r'\d+'),
    ('ID',        r'[A-Za-z_][A-Za-z0-9_]*'),
    ('COMPOUND',  r'\+=|-=|\*=|/='),
    ('OP',        r'==|!=|<=|>=|\+\+|--|&&|\|\||[+\-*/<>]'),
    ('ASSIGN',    r'='),
    ('NEWLINE',   r'\n'),
    ('SKIP',      r'[ \t]+'),
    ('SYMBOL',    r'[;(){}]'),
    ('MISMATCH',  r'.'),
]

regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)

# 1. MODIFIKASI COPY_RANGE agar map_code hanya diisi pertama & terakhir
def copy_range(start, end, offset, code, map_code, map_pre, cleaned):    
    # map_code hanya diisi indeks pertama dan indeks terakhir dari token ini
    # map_code.extend([start + offset, (end - 1) + offset])
    
    # map_pre tetap dibiarkan per karakter agar sinkron dengan cleaned_code
    rng_pre = [i + offset for i in range(start, end)]
    map_pre.extend(rng_pre)
    
    cleaned.extend(code[start:end])

def tokenize(code: str, tpe, mapping_doc_counter, mapping_code_counter, mapping_code_hash_counter, mapping_image_counter, keywords: set = KEYWORDS):

    mapping_preprocess_temp = []
    mapping_preprocess_temp_extend = mapping_preprocess_temp.extend

    mapping_doc_temp = []
    mapping_doc_temp_append = mapping_doc_temp.append

    mapping_code_temp = []

    # 1. INISIALISASI LIST UNTUK HASH TEMP
    mapping_hash_temp = []

    cleaned_code = []
    cleaned_code_extend = cleaned_code.extend

    # Catat indeks paling pertama dari seluruh kode asli
    indeks_awal_total = mapping_code_counter

    # 2. CATAT INDEKS AWAL DARI CLEANED CODE (Berdasarkan counter global hash)
    indeks_awal_hash = mapping_code_hash_counter

    for m in re.finditer(regex, code):

        kind  = m.lastgroup
        value = m.group()
        
        if tpe == 'TYPING':
            for i in range(m.start(), m.end()):
                mapping_doc_temp_append(i + mapping_doc_counter)
        else:
            for i in range(m.start(), m.end()):
                mapping_doc_temp_append(i + mapping_image_counter)

        if kind == 'NEWLINE':
            continue

        elif kind in ('SKIP', 'COMMENT', 'MCOMMENT'):
            continue

        elif kind == 'UNTERM_STR':
            copy_range(
                m.start(), m.end(), mapping_code_counter,
                code,
                mapping_code_temp,
                mapping_preprocess_temp,
                cleaned_code
            )

        elif kind == 'MISMATCH':
            copy_range(
                m.start(), m.end(), mapping_code_counter,
                code,
                mapping_code_temp,
                mapping_preprocess_temp,
                cleaned_code
            )

        elif kind == 'ID':
            if value in keywords:
                copy_range(
                    m.start(), m.end(), mapping_code_counter,
                    code,
                    mapping_code_temp,
                    mapping_preprocess_temp,
                    cleaned_code
                )
            else:
                special_map = mapping_code_counter + m.start()
                mapping_preprocess_temp_extend([special_map, special_map, special_map])
                cleaned_code_extend(['V', 'A', 'R'])

        elif kind in ('NUMBER', 'FLOAT'):
            special_map = mapping_code_counter + m.start()
            mapping_preprocess_temp_extend([special_map, special_map, special_map])
            cleaned_code_extend(['N', 'U', 'M'])

        elif kind == 'STRING':
            special_map = mapping_code_counter + m.start()
            mapping_preprocess_temp_extend([special_map, special_map, special_map])
            cleaned_code_extend(['S', 'T', 'R'])

        else:
            copy_range(
                m.start(), m.end(), mapping_code_counter,
                code,
                mapping_code_temp,
                mapping_preprocess_temp,
                cleaned_code
            )

    # 3. PROSES SETELAH LOOP SELESAI
    
    # Hitung indeks akhir untuk kode asli
    indeks_akhir_total = indeks_awal_total + len(code) - 1
    mapping_code_temp = [indeks_awal_total, indeks_akhir_total]

    # Hitung indeks akhir untuk cleaned_code
    # len(cleaned_code) adalah jumlah total elemen karakter di dalam list bersih
    if len(cleaned_code) > 0:
        indeks_akhir_hash = indeks_awal_hash + len(cleaned_code) - 1
        mapping_hash_temp = [indeks_awal_hash, indeks_akhir_hash]
    else:
        # Jika kodenya kosong (misal cuma spasi/komentar saja), isi dengan indeks awal saja
        mapping_hash_temp = [indeks_awal_hash, indeks_awal_hash]

    # 4. TAMBAHKAN MAPPING_HASH_TEMP KE RETURN VALUE
    return mapping_doc_temp, mapping_code_temp, mapping_preprocess_temp, mapping_hash_temp, cleaned_code


# kk = """
# int Data[MAX];
# int x = 0;
# int y = 0;
# """

# kkk = """
# int Data[MAX];
# int x = 0;
# int y = 0;

# void Tukar(int *a, int *b) {
#     int temp;

#     temp = *a;
#     *a = *b;
#     *b = temp;
# }
# """
# coba = tokenize(kk, "IMAGE", 10, 38, 1)
# print(coba[3])