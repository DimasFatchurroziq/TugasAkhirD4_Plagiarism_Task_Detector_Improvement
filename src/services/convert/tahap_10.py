import base64
import fitz  # PyMuPDF
from src.infrastructures.reverse.generate import generate_tuple_color, convert_pdf_font_to_css, rgb_to_hex
from src.infrastructures.preprocessing.text_normalize import clean_pdf_text


class Tahap_10:

    def extract_pdf_to_data(self, filePDF, list_match_typing_mapping, list_match_image_mapping, list_image_content):

        # print(list_image_content)
        
        target_ranges_typing = generate_tuple_color(list_match_typing_mapping)
        target_ranges_image = generate_tuple_color(list_match_image_mapping)

        BG_TARGETS_TYPING = {}
        for (start, end), color in target_ranges_typing.items():
            for num in range(start, end + 1):
                BG_TARGETS_TYPING[num] = color

        BG_TARGETS_IMAGE = {}
        for (start, end), color in target_ranges_image.items():
            for num in range(start, end + 1):
                BG_TARGETS_IMAGE[num] = color
        
        # print(BG_TARGETS_IMAGE)


        doc = fitz.open(filePDF)
        pages_data = []
        map_doc_counter = 0
        map_image_counter = 0
        image_content = 0

        for page_index, page in enumerate(doc):
            page_rawdict = page.get_text("rawdict")
            
            page_item = {
                "index": page_index,
                "width": page.rect.width,
                "height": page.rect.height,
                "characters": [],
                "images": []
            }

            if page_index > 0:
                for block in page_rawdict["blocks"]:
                    if block["type"] == 0:  # Text block
                        for line in block["lines"]:
                            for span in line["spans"]:
                                font_size = span["size"]
                                css_result = convert_pdf_font_to_css(span["font"])
                                color = "#000000"
                                
                                for char in span["chars"]:
                                    c_text = clean_pdf_text(char["c"])

                                    if c_text == "":
                                        continue

                                    bg_color = "transparent"
                                    if map_doc_counter in BG_TARGETS_TYPING:
                                        bg_color = BG_TARGETS_TYPING[map_doc_counter]

                                    map_doc_counter += 1

                                    # Simpan data tiap karakter ke dalam dictionary
                                    page_item["characters"].append({
                                        "text": c_text,
                                        "x0": char["bbox"][0],
                                        "y0": char["bbox"][1],
                                        "font_size": font_size,
                                        "color": color,
                                        "css_result": css_result,
                                        "bg_color": bg_color
                                    })

                    # elif block["type"] == 1:
                    elif block["type"] == 1:  # <--- TAMBAHAN: Logika Ekstrak Gambar

                        text_image = []

                        bbox = block["bbox"]
                        box_width = bbox[2] - bbox[0]
                        box_height = bbox[3] - bbox[1]

                        # Encode image bytes ke base64 string
                        base64_str = base64.b64encode(
                            block["image"]
                        ).decode("utf-8")
                        image_format = block["ext"]  # 'png', 'jpeg', dll.

                        if image_content < len(list_image_content):
                            for char in list_image_content[image_content]:
                                bg_color = "transparent"
                                if map_image_counter in BG_TARGETS_IMAGE:
                                    bg_color = BG_TARGETS_IMAGE[map_image_counter]
                                map_image_counter += 1

                                text_image.append({
                                    "text": char,
                                    "font_size": '12px',
                                    "color": '#000000',
                                    "font_family": 'Courier New',
                                    "bg_color": bg_color
                                })
                        else:
                            # Log jika ternyata gambar di PDF melebihi kapasitas data teks OCR gambar
                            print(f"[WARNING] Gambar ke-{image_content} dilewati karena list_image_content habis.")
                        
                        image_content += 1

                        # for char in list_image_content[image_content]:
                        #     bg_color = "transparent"
                        #     if map_image_counter in BG_TARGETS_IMAGE:
                        #         bg_color = BG_TARGETS_IMAGE[map_image_counter]

                        #         map_image_counter += 1

                        #     text_image.append({
                        #         "text": char,
                        #         "font_size": '12px',
                        #         "color": '#000000',
                        #         "font_family": 'Courier New',
                        #         "bg_color": bg_color
                        #     })
                        
                        # image_content += 1

                        page_item["images"].append({
                            "x0": bbox[0],
                            "y0": bbox[1],
                            "box_width": box_width,
                            "box_height": box_height,
                            "format": image_format,
                            "base64_data": f"data:image/{image_format};base64,{base64_str}",
                            "text_image": text_image
                        })

                                    
                pages_data.append(page_item)

            else:
                for block in page_rawdict["blocks"]:
                    if block["type"] == 0:  # Text block
                        for line in block["lines"]:
                            for span in line["spans"]:
                                font_size = span["size"]
                                css_result = convert_pdf_font_to_css(span["font"])
                                color = "#000000"
                                
                                for char in span["chars"]:
                                    bg_color = "transparent"

                                    # Simpan data tiap karakter ke dalam dictionary
                                    page_item["characters"].append({
                                        "text": char["c"],
                                        "x0": char["bbox"][0],
                                        "y0": char["bbox"][1],
                                        "font_size": font_size,
                                        "color": color,
                                        "css_result": css_result,
                                        "bg_color": bg_color
                                    })

                    elif block["type"] == 1:  # <--- TAMBAHAN: Logika Gambar di Halaman Pertama
                        bbox = block["bbox"]
                        box_width = bbox[2] - bbox[0]
                        box_height = bbox[3] - bbox[1]

                        base64_str = base64.b64encode(
                            block["image"]
                        ).decode("utf-8")
                        image_format = block["ext"]

                        page_item["images"].append({
                            "x0": bbox[0],
                            "y0": bbox[1],
                            "box_width": box_width,
                            "box_height": box_height,
                            "format": image_format,
                            "base64_data": f"data:image/{image_format};base64,{base64_str}",
                        })
                                    
                pages_data.append(page_item)

        # print(map_doc_counter)

        doc.close()
        return pages_data


