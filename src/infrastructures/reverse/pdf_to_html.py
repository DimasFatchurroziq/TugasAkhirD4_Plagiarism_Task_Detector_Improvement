import fitz  # PyMuPDF
from src.infrastructures.reverse.pdf_to_html import extract_pdf_to_data


def convert_to_html(list_match_mapping):

    target_ranges = generate_tuple_color(list_match_mapping)

    BG_TARGETS = {}
    for (start, end), color in target_ranges.items():
        for num in range(start, end + 1):
            BG_TARGETS[num] = color


    doc = fitz.open("3123510310.pdf")

    html_output = []

    # Header HTML
    html_output.append("""<!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    body {
        background: #f0f0f0;
    }
    .page {
        position: relative;
        margin: 20px auto;
        background: white;
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
    }
    @media print {
        .page {
            page-break-after: always;
            box-shadow: none;
            margin: 0;
        }
    }
    </style>
    </head>
    <body>
    """)

    map_doc_counter = 0

    # Loop halaman
    for page_index, page in enumerate(doc):
        page_rawdict = page.get_text("rawdict")
        page_width = page.rect.width
        page_height = page.rect.height

        html_output.append(f"""
    <div class="page"
        id="page-{page_index}"
        data-page="{page_index+1}"
        style="width:{page_width}pt;height:{page_height}pt;">
    """)

        for block in page_rawdict["blocks"]:
            if block["type"] != 0:
                x0, y0, x1, y1 = block["bbox"]
                w = x1 - x0
                h = y1 - y0

                # Ambil data biner gambar
    #             image_bytes = block["image"]
    #             image_ext = block["ext"]  # ekstensi gambar (png, jpeg, dll)

    #             # Simpan gambar ke dalam folder
    #             image_filename = f"extracted_images/img_{page_index}_{image_counter}.{image_ext}"
    #             with open(image_filename, "wb") as f_img:
    #                 f_img.write(image_bytes)

    #             image_counter += 1

    #             # Masukkan gambar ke HTML dengan posisi absolut sesuai PDF
    #             html_output.append(f"""
    # <img src="{image_filename}" style="
    #     position: absolute;
    #     left: {x0}pt;
    #     top: {y0}pt;
    #     width: {w}pt;
    #     height: {h}pt;
    # ">
    # """)


            elif block["type"] == 0:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_size = span["size"]
                        css_result = convert_pdf_font_to_css(span["font"])
                        color = rgb_to_hex(span["color"])
                        print(css_result)
                        for char in span["chars"]:
                            text = char["c"]
                            x0, y0, x1, y1 = char["bbox"]

                            if map_doc_counter in BG_TARGETS:
                                bg_color = BG_TARGETS[map_doc_counter]

                            map_doc_counter += 1

                            html_output.append(f"""
    <p style="
        position:absolute;
        left:{x0}pt;
        top:{y0}pt;
        font-size:{font_size}pt;
        color:{color};
        {css_result};
        background-color: {bg_color};
        margin:0;
    ">
    {text}
    </p>
    """)

        html_output.append("</div>")

    # Footer
    html_output.append("</body></html>")

    doc.close()

    # Simpan file
    with open("otput.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html_output))

    print("Selesai convert ke output.html")




def extract_pdf_to_data(pdf_bytes, list_match_mapping):
    target_ranges = generate_tuple_color(list_match_mapping)
    BG_TARGETS = {}
    for (start, end), color in target_ranges.items():
        for num in range(start, end + 1):
            BG_TARGETS[num] = color

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_data = []
    map_doc_counter = 0

    for page_index, page in enumerate(doc):
        page_rawdict = page.get_text("rawdict")
        
        page_item = {
            "index": page_index,
            "width": page.rect.width,
            "height": page.rect.height,
            "characters": []
        }

        for block in page_rawdict["blocks"]:
            if block["type"] == 0:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_size = span["size"]
                        css_result = convert_pdf_font_to_css(span["font"])
                        color = rgb_to_hex(span["color"])
                        
                        for char in span["chars"]:
                            bg_color = "transparent"
                            if map_doc_counter in BG_TARGETS:
                                bg_color = BG_TARGETS[map_doc_counter]

                            map_doc_counter += 1

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
                            
        pages_data.append(page_item)

    doc.close()
    return pages_data


