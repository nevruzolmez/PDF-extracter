from flask import Flask
import urllib.request
import os
import fitz

app = Flask(__name__)

@app.route('/pdfparse/<path:url_string>')

def pdf_parser(url_string):
    # declare space_checker array, if there are other notations for spacing, add to this array
    space_checker = ["\xa0", " "]
    # to get the pdf from the url provided
    pdf_path = url_string
    urllib.request.urlretrieve(pdf_path, "filename.pdf")
    # open the pdf with fitz
    doc = fitz.open("filename.pdf")
    total_page = doc.page_count
    json_data = {}
    page_counter = 0
    for page in doc:
        page_counter +=1
        if page_counter > 3 and page_counter < total_page-1: continue
        json_data[page_counter] = []
        page_data = json_data[page_counter]
        words = page.get_text("dict")
        print(words)
        for block in words["blocks"]:
            #to check if the block is image, if type == 1, block is image so continue
            if(block["type"] == 1): continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    x0, y0, x1, y1 = span['bbox']
                    len_text = len(text)
                    width = x1 - x0
                    #to replace unknown spacing
                    for space in space_checker:
                        text = text.replace(space,"\t")
                    split_text = text.split("\t")
                    #Check if text is splitted with \t
                    if len(split_text) == 1:
                        split_text = text.split(" ")
                        #Check if text is splitted with " "
                        if len(split_text) == 1:
                            data = {'text': text, 'x0': round(x0), 'y0': round(y0), 'x1': round(x1), 'y1': round(y1)}
                            page_data.append(data)
                        else:
                            len_per_letter = width / len_text
                            pdf_split(split_text,page_data,len_per_letter,x0,y0,x1,y1)
                    else:
                        len_per_letter = width / len_text
                        pdf_split(split_text,page_data,len_per_letter,x0,y0,x1,y1)
    #close the document & remove the pdf file
    doc.close()
    os.remove("filename.pdf")
    return json_data
if __name__ == '__main__':
    app.run()

#function for splitted array to update their coordinates and add it to page object
def pdf_split (split_array, page_object, len_per_letter,x0,y0,x1,y1):
    for word in split_array:
        if(word == " " or word == "*" or word == ""): continue  
        word_len = len(word)
        x1 = x0 + word_len * len_per_letter
        data = {'text': word, 'x0': round(x0), 'y0': round(y0), 'x1': round(x1), 'y1': round(y1)}
        page_object.append(data)
        x0 = x1 + len_per_letter

