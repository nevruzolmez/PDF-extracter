from flask import Flask
import urllib.request
import os
import fitz

app = Flask(__name__)

@app.route('/pdfparse/<path:url_string>')

def pdf_parser(url_string):
    # to get the pdf from the url provided
    pdf_path = url_string
    urllib.request.urlretrieve(pdf_path, "filename.pdf")
    # open the pdf with fitz
    doc = fitz.open("filename.pdf")
    json_data = {}
    page_counter = 0
    for page in doc:
        page_counter +=1
        json_data[page_counter] = []
        page_data = json_data[page_counter]
        words = page.get_text("dict")
        for block in words["blocks"]:
            if(block["type"] == 1): continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    x0, y0, x1, y1 = span['bbox']
                    len_text = len(text)
                    width = x1 - x0
                    split_text = text.split("\t")
                    if len(split_text) == 1:
                        data = {'text': text, 'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1}
                        page_data.append(data)
                    else:
                        len_per_letter = width / len_text
                        for word in split_text:
                            if(word == " " or word == "*" or word == ""): continue
                            word_len = len(word)
                            x1 = x0 + word_len * len_per_letter
                            data = {'text': word, 'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1}
                            page_data.append(data)
                            x0 = x1 + len_per_letter
    #close the document & remove the pdf file
    doc.close()
    os.remove("filename.pdf")
    return json_data
if __name__ == '__main__':
    app.run()

