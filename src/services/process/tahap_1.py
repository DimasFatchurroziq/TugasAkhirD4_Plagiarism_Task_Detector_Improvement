import fitz
import pytesseract
from fastapi.concurrency import run_in_threadpool
from src.infrastructures.extraction.ocr import ocr_code_image

from src.infrastructures.preprocessing.text_normalize import clean_pdf_text
from src.infrastructures.extraction.re import classify_typing_true, classify_typing_false, classify_image, _is_monospace, classify_list_content


class Tahap_1:

    # def __init__(self, document_repository):
    #     self.document_repository = document_repository

    # ======================
    # MAIN FUNCTION
    # ======================
    async def structure_extract(self, filePDF):

        list_blocks = []
        saved_xrefs = set()

        doc = fitz.open(filePDF)

        try:

            # ======================
            # LOOP PAGE
            # ======================
            
            all_extarcted = []

            all_image_clas = []

            all_fonts = []

            for page_num, page in enumerate(doc[1:], start=2):

                data = page.get_text("dict", sort=True)

                extracted = []

                # ======================
                # LOOP BLOCK
                # ======================
                for block in data.get("blocks", []):

                    # ======================
                    # TEXT BLOCK
                    # ======================
                    if block.get("type") == 0:

                        block_segments = []
                        current_segment = None

                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                tex = span.get("text", "")
                                text = clean_pdf_text(tex)

                                # if not text.strip():
                                #     continue

                                font = span.get("font")
                                size = int(span.get("size"))

                                # cek apakah bisa digabung
                                if current_segment:
                                    if (
                                        current_segment["font"] == font and
                                        current_segment["size"] == size
                                    ):
                                        current_segment["content"] += text
                                        current_segment["content_merge"] += "||~MERGE~||" + text
                                    else:
                                        block_segments.append(current_segment)
                                        current_segment = {
                                            "content": text,
                                            "font": font,
                                            "size": size,
                                            "source": "TYPING",
                                            "content_merge": text
                                        }
                                else:
                                    current_segment = {
                                        "content": text,
                                        "font": font,
                                        "size": size,
                                        "source": "TYPING",
                                        "content_merge": text
                                    }

                        if current_segment:
                            block_segments.append(current_segment)

                        if block_segments:
                            extracted.extend(block_segments)


                    # ======================
                    # IMAGE BLOCK
                    # ======================
                    elif block.get("type") == 1:
                        # print("gambar")

                        img_bytes = None

                        # CASE 1: xref
                        if "xref" in block:
                            xref = block["xref"]

                            if xref in saved_xrefs:
                                continue

                            saved_xrefs.add(xref)

                            img = doc.extract_image(xref)
                            img_bytes = img["image"]

                        # CASE 2: inline
                        elif "image" in block:
                            img_bytes = block["image"]

                        if img_bytes is None:
                            continue

                        # ======================
                        # OCR (FIXED)
                        # ======================
                        ocr_text = await run_in_threadpool(
                            ocr_code_image,
                            img_bytes
                        )

                        # ocr_text = ocr_code_image(img_bytes)

                        if not ocr_text:
                            continue

                        extracted.append({
                            "content": ocr_text,
                            "font": "ocr_font",
                            "size": "ocr_size",
                            "source": "IMAGE",
                            "content_merge": ocr_text
                        })

                # ======================
                # SAFETY CHECK
                # ======================
                if not extracted:
                    continue

                all_extarcted.append(extracted)

                fonts = [item.get("font") for item in extracted] 
                fonts_list = [f.strip() for item in fonts for f in item.split(',')]    
                all_fonts.extend(fonts_list)               

                # ======================
                # GROUPING SAFE
                # ======================
                # result = []
                # temp = extracted[0]

                # for block in extracted[1:]:

                #     if (
                #         # len(temp["content"]) < 60 and
                #         set(temp["font"]) == set(block["font"]) and
                #         temp["source"] == block["source"]
                #     ):
                #         temp["content"] += block["content"]
                #     else:
                #         result.append(temp)
                #         temp = block

                # result.append(temp)

            # ======================
            # CLASSIFICATION
            # ======================

            # for extracted in all_extarcted:            
            #     for block in extracted:
            #         if block["source"] == "TYPING":
            #             continue

            #         elif block["source"] == "IMAGE":
            #             block_type, confidence, language = classify_image(
            #                 block["content"],
            #                 block["font"]
            #             )

            #         all_image_clas.append([block_type, confidence, language])

            # assigned_class = classify_list_content(all_image_clas)

            text_clas = _is_monospace(all_fonts)

            for extracted in all_extarcted:            
                for block in extracted:
                    if block["source"] == "TYPING":
                        if text_clas:
                            # print("1")
                            block_type, confidence, language = classify_typing_true(
                                block["content"],
                                block["font"]
                            )
                        else:
                            # print("2")
                            block_type, confidence, language = classify_typing_false(
                                block["content"],
                                block["font"]
                            )

                        
                        if block_type == "TEXT":

                            list_blocks.append({
                                "content": block["content"],
                                "type": block_type,
                                "confidence": confidence,
                                "language": language,
                                "source": block["source"],
                                "font": block["font"]
                            })

                        elif block_type == "CODE":

                            teks_berstruktur = block["content_merge"].replace("||~MERGE~||", "\n")
                            
                            list_blocks.append({
                                "content": teks_berstruktur,
                                "type": block_type,
                                "confidence": confidence,
                                "language": language,
                                "source": block["source"],
                                "font": block["font"]
                            })

                    elif block["source"] == "IMAGE":
                        block_type, confidence, language = classify_image(
                            block["content"],
                            block["font"]
                        )

                        list_blocks.append({
                            "content": block["content"],
                            "type": block_type,
                            "confidence": confidence,
                            "language": language,
                            "source": block["source"],
                            "font": block["font"]
                        })

        finally:
            doc.close()

        # print("tah1")
        # print(all_image_clas)
        return list_blocks