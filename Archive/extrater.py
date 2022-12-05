import mammoth
import re

#input_filename  = "fullfile/75_29-11.docx"
input_filename  = "fullfile/75_29-11_xxxv.docx"
#output_filename = "fullfile/output"
output_filename = "fullfile/output_xxxv"
qnt_modalidades = 0

def extract_text():
    print("extraindo txt...")
    with open(input_filename, "rb") as docx_file:
        result = mammoth.extract_raw_text(docx_file)
        text = result.value

        #modalidades = re.findall(r'Modalidade', text)
        #qnt_modalidades = len(modalidades)
        #print(f"Foram encontradas {qnt_modalidades} modalidades nesse arquivo.")

        with open(f"{output_filename}.txt", 'w') as text_file:
            text_file.write(text)
        #
    #
    print("txt extraido!")
#

def extract_html():
    print("extraindo html...")
    with open(input_filename, "rb") as docx_file:
        result = mammoth.convert_to_html(docx_file)
        text = result.value
        with open(f"{output_filename}.html", 'w') as html_file:
            html_file.write(text)
        #
    #
    print("html extraido!")
#

print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
print(f"Arquivo: {input_filename}")
#extract_text()
extract_html()

print("Fim do programa")
