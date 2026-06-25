# @@@@ tahap 2
# preprosesing
# (mapping, sentence)

from src.infrastructures.preprocessing.case_transform import change_to_lowercase, change_to_uppercase
from src.infrastructures.preprocessing.text_normalize import remove_special_character
from src.infrastructures.preprocessing.text_tokenize import tokenize_word, tokenize_sentence, tokenize_character
from src.infrastructures.preprocessing.lexer import tokenize
from src.infrastructures.preprocessing.penyama import penggabung

from src.utils.mapping import mapping

class Tahap_2:

    async def preprocessing(self, list_blocks):

        # kon =0

        final_result = []
        final_mapping = []

        final_data = []

        mapping_doc_counter = 0  # counter doc global
        mapping_image_counter = 0  # counter isi image global
        order_block = 1 # order global

        mapping_text_counter = 0 #counter text global
        mapping_text_hash_counter = 0 #counter text hash global
        full_cleaned_text = []
        full_cleaned_text_append = full_cleaned_text.append #ini yg dikirim langsung ke tahap 3 tanpa masuk database

        mapping_code_counter = 0 #counter code global
        mapping_code_hash_counter = 0 #counter code hash global
        full_cleaned_code = []
        full_cleaned_code_extend = full_cleaned_code.extend #ini yg dikirim langsung ke tahap 3 tanpa masuk database

        list_blocks = penggabung(list_blocks)

        full_cleaned = []

        sequence = 0

        for block in list_blocks:
            if block["type"] == "TEXT":
                sentence_tokens = tokenize_sentence(block["content"])
                for sentence in sentence_tokens:

                    char = ""
                    
                    mapping_doc_text_temp = []
                    mapping_doc_text_temp_append = mapping_doc_text_temp.append

                    mapping_text_temp = []
                    
                    mapping_preprocess_text_temp = []
                    mapping_preprocess_text_temp_append = mapping_preprocess_text_temp.append

                    mapping_hash_text_temp = []

                    lower_sentence = change_to_lowercase(sentence)

                    first_text_index = mapping_text_counter

                    first_hash_index = mapping_text_hash_counter

                    for ch in lower_sentence:
                        if ch.isalnum() or ch.isspace(): #ini harus di ganti
                            char += ch

                            # first_hash_index = mapping_text_hash_counter

                            if ch.isalnum():
                                full_cleaned_text_append(ch)
                                mapping_preprocess_text_temp_append(mapping_text_counter)

                                mapping_text_hash_counter += 1
                            
                            # last_hash_index = mapping_text_hash_counter - 1

                            # mapping_hash_text_temp = [first_hash_index, last_hash_index]

                        mapping_doc_text_temp_append(mapping_doc_counter)

                        mapping_text_counter += 1
                        mapping_doc_counter += 1

                    last_text_index = mapping_text_counter - 1

                    mapping_text_temp = [first_text_index, last_text_index]

                    last_hash_index = mapping_text_hash_counter - 1

                    if last_hash_index < first_hash_index:
                        mapping_hash_text_temp = [first_hash_index, first_hash_index]
                    else:
                        mapping_hash_text_temp = [first_hash_index, last_hash_index]

                    if char.strip():   # <- ini yang mencegah baris kosong masuk

                        sequence += 1

                        final_data.append({
                            "block": {
                                "sequence": sequence,
                                "content": char.strip(),
                                "type": block["type"],
                                "source": block["source"]
                            },
                            "mapping": {
                                "mapping_doc": mapping_doc_text_temp,
                                "mapping_text_code": mapping_text_temp,
                                "mapping_preprocess": mapping_preprocess_text_temp,
                                "mapping_hash": mapping_hash_text_temp
                            }
                        })

            elif block["type"] == "CODE":
                
                mapping_doc_code_temp, mapping_code_temp, mapping_preprocess_code_temp, mapping_hash_code_temp, cleaned_code = tokenize(block["content"], block["source"], mapping_doc_counter, mapping_code_counter, mapping_code_hash_counter, mapping_image_counter)

                
                # if kon == 0:
                #     print(mapping_doc_code_temp, block["source"], mapping_doc_counter, mapping_code_counter, mapping_code_hash_counter, mapping_image_counter)
                # # print(mapping_doc_code_temp, mapping_code_temp, mapping_preprocess_code_temp, mapping_hash_code_temp, cleaned_code)
                # kon += 1

                full_cleaned_code_extend(cleaned_code)
                
                mapping_code_counter = mapping_code_temp[1] + 1
                mapping_code_hash_counter = mapping_hash_code_temp[1] + 1

                if block["source"] == "IMAGE":
                    # mapping_doc_counter += 1
                    mapping_image_counter += len(mapping_doc_code_temp)
                else:
                    mapping_doc_counter += len(mapping_doc_code_temp)

                sequence += 1

                final_data.append({
                    "block": {
                        "sequence": sequence,
                        "content": block["content"],
                        "type": block["type"],
                        "source": block["source"]
                    },
                    "mapping": {
                        "mapping_doc": mapping_doc_code_temp,
                        "mapping_text_code": mapping_code_temp,
                        "mapping_preprocess": mapping_preprocess_code_temp,
                        "mapping_hash": mapping_hash_code_temp
                    }
                })  

            elif block["type"] == "TERMINAL":

                mapping_doc_terminal_temp = []
                mapping_doc_terminal_temp_append = mapping_doc_terminal_temp.append

                for i in range(len(block["content"])):
                    mapping_doc_terminal_temp_append(i + mapping_image_counter) 
                
                mapping_image_counter += len(mapping_doc_terminal_temp)
                # mapping_doc_counter += 1

                sequence += 1

                final_data.append({
                    "block": {
                        "sequence": sequence,
                        "content": block["content"],
                        "type": block["type"],
                        "source": block["source"]
                    },
                    "mapping": {
                        "mapping_doc": mapping_doc_terminal_temp,
                        "mapping_text_code": [-1,-1],
                        "mapping_preprocess": [-1,-1],
                        "mapping_hash": [-1,-1]
                    }
                }) 

                
        full_cleaned = {
            "full_cleaned_text": full_cleaned_text,
            "full_cleaned_code": full_cleaned_code
        }

        return final_data, full_cleaned            

