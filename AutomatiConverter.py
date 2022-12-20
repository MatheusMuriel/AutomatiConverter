import os
import shutil
import re
import sys
import subprocess
from bs4 import BeautifulSoup
from slugify import slugify
from Utils.colors import *
from Utils.roman import *
from Utils.lambdas import *
from Modules.Corretores import *
from Modules.Renamings import *


# Referencias e Documentações
# https://pandoc.org/try/
# https://www.uv.es/wikibase/doc/cas/pandoc_manual_2.7.3.wiki
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/

environment_is_dev = True

docx_input_folder   = "DOCX"
html_output_folder  = "HTML"
sql_output_folder   = "SQL"
csv_input_folder    = "CSV"

branch_list = [
    {
        "ramo": "75",
        "category_code_start": 92,
        "modality_order_code_start": 14,
        "input_file": "75_29-11.docx",
        "sql_output_file": "output75.sql"
    },
    {
        "ramo": "76",
        "category_code_start": 133,
        "modality_order_code_start": 55,
        "input_file": "04-76_05-12.docx",
        "sql_output_file": "output76.sql"
    }
]

## End Parametrização

def converter():

    print(bold(":::::::::::::::::::::::::"))
    print("Iniciando conversão via pandoc...")
    print(f"Arquivo de entrada: {underline(input_file)}")
    print(yellow("Executando o comando..."))
    print(bold(f"pandoc --from docx --to html5 --no-highlight -o {html_output_file} {input_file}"))
    os.system(f"pandoc --from docx --to html5 --no-highlight -o {html_output_file} {input_file}")
    print(green("Comando executado com sucesso"))
    print(f"Gerado o arquivo {underline(html_output_file)}")
#

def spliter():
    print(bold(":::::::::::::::::::::::::"))
    print("Iniciando a etapa de Split...")

    with open(html_output_file, "r", encoding='utf-8') as html_file:
        html_doc = html_file.read()
        html_file.close()
    #

    parsed_html = BeautifulSoup(html_doc, 'html.parser')
    print(green(f"Parserizado o arquivo {html_output_file}"))

    modalidades = parsed_html.find_all(lambda tag: is_modalidade_title(tag))

    for m in modalidades[1:]:
        m.parent.insert_before("###DIVIDER###")
    #

    str_html = str(parsed_html)
    str_html = str_html.replace('\n',' ')
    pages = str_html.split("###DIVIDER###")
    print(f"Dividido em {bold(len(pages))} partes")

    print(yellow("Salvando arquivos..."))
    for index,page in enumerate(pages):
        parsed_page = BeautifulSoup(page, 'html.parser')
        title = parsed_page.find(lambda t: is_modalidade_title(t))
        
        roman_number_regex = "\sM{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\s"
        search_result = re.search(roman_number_regex, title.text.upper())
        modalite_number = ''
        if search_result is not None:
            roman_number = search_result.group().replace(" ","")
            modalite_number = romanToDecimal(roman_number)        
            file_name = f"{modalite_number:02d}_{slugify(title.text)}.html"
            with open(f"{modalidades_path}/{file_name}", 'w') as html_file:
                html_file.write(page)
        else:
            print(red(f"Numero romano não encontrado no arquivo: {title.text}"))
            #file_name = f"{slugify(title.text)}.html"
        #file_name = f"{index}_{slugify(title.text)}.html"
        #with open(f"{modalidades_path}/{file_name}", 'w') as html_file:
            #html_file.write(page)
        #
    #
    print(green("Arquivos salvos."))
#

def corretor():
    print(bold(":::::::::::::::::::::::::"))
    print("Iniciando o etapa de Correção...")
    modalidades_files = os.listdir(modalidades_path)
    if '.gitkeep' in modalidades_files: 
        modalidades_files.remove('.gitkeep')
    
    print(f"Foram encontrados {bold(len(modalidades_files))} arquivos de modalidade")
    for index,modalidade_file_name in enumerate(modalidades_files):
        modalidade = open(f"{modalidades_path}/{modalidade_file_name}", "r")
        modalidade_html = modalidade.read()
        modalidade.close()
        
        print(blue(f"{index+1} - {modalidade_file_name}"))
        html = BeautifulSoup(modalidade_html, 'html.parser')
        
        # Correctores de HTML
        html = corrector_modality_header(html)
        html = corrector_topic_title(html)
        html = corrector_spacing_alphabetic_list_itens(html)
        html = corrector_indentation_alphabetic_lists(html)
        html = corrector_numbered_lists_after_alphabetic_list(html)
        html = corrector_font_swiss_sans(html)
        html = corrector_converter_nested_list(html)

        # Correctores de String
        output_html = str(html)
        output_html = corrector_invalid_characters(output_html)

        print(yellow("Salvando arquivo..."))
        modalidade = open(f"{modalidades_path}/{modalidade_file_name}", "w")
        modalidade.write(output_html)
        modalidade.close()
        print(green("Arquivo salvo."))
    #
    print(green("Fim da etapa de Correção."))
#

def sqler():
    #input("Verifique os arquivos html e se estiver certo aparte enter para continuar com o modulo SQLer...")
    print(bold(":::::::::::::::::::::::::"))
    print("Iniciando o modulo de SQL")
    modalidades_files = os.listdir(modalidades_path)
    if '.gitkeep' in modalidades_files: 
        modalidades_files.remove('.gitkeep')
    print(f"Foram encontrados {bold(len(modalidades_files))} arquivos de modalidade")

    category_code = current_branch["category_code_start"]
    modality_order_code = current_branch["modality_order_code_start"]

    declarers = []
    inserts = []
    for modalidade_file_name in modalidades_files:
        with open(f"{modalidades_path}/{modalidade_file_name}", "r") as modalidade:
            modalidade_html = modalidade.read()
            modalidade.close()
        #
        modality_number = modalidade_file_name.split("_")[0]
        str_declare = f"DECLARE @Modality_{ramo}_{modality_number} VARCHAR(MAX) = '{modalidade_html}';"
        declarers.append(str_declare)

        parsed_html = BeautifulSoup(modalidade_html, 'html.parser')

        modalidade_title = parsed_html.find(lambda tag: is_modalidade_title(tag)).string
        modalidade_title = get_renamed_title_for(modalidade_title, renamings_list)
        # @CategoryCodeCounter :: @ModalityOrderCounter
        str_insert = f"EXEC #ConfigureModalitiesForCircular662 @ProductCode,'{modalidade_title}', '{category_code:03d}', '{modality_order_code:02d}', @InitialDate, @Modality_{ramo}_{modality_number};"
        category_code += 1
        modality_order_code += 1
        inserts.append(str_insert)
    #
    
    str_declarer = '\n'.join(declarers)
    str_set_product = "SET @ProductCode = '77777';"
    str_insert = '\n'.join(inserts)
    
    str_final = f"{str_declarer}\n{str_set_product}\n{str_insert}"

    with open(f"{sql_output_file}", 'w') as sql_file:
        sql_file.write(str_final)
    #
#

def validator():
    print(bold(":::::::::::::::::::::::::"))
    print("Iniciando o modulo Validator")
    modalidades_files = os.listdir(modalidades_path)
    print(f"Foram encontrados {bold(len(modalidades_files))} arquivos de modalidade")
    pwd = os.getcwd()
    pwd = pwd.replace("\\", "/")
    url_file_list = f"file:///{pwd}/{modalidades_path}"
    print(f"Abrindo o navegador na pasta {url_file_list} para vizualizar os arquivos")
    subprocess.call(f'firefox {url_file_list}', shell=True)
#

## ----------------------------------------------------
for index,current_branch in enumerate(branch_list):
    input_file_name     = current_branch['input_file']
    ramo                = current_branch["ramo"]
    input_file          = f"{docx_input_folder}/{input_file_name}"
    input_file_folder   = f"{html_output_folder}/{input_file_name.split('.')[0]}"
    sql_output_file     = f"{sql_output_folder}/{current_branch['sql_output_file']}"
    html_output_file    = f"{input_file_folder}/output_full.html"
    modalidades_path    = f"{input_file_folder}/Modalidades"
    csv_renamings_file  = f"{csv_input_folder}/DePara-Modalidades.csv"

    renamings_list = prepare_list_of_renamings(csv_renamings_file)

    ### Clean folders before execution
    if os.path.exists(input_file_folder) and not environment_is_dev:
        shutil.rmtree(input_file_folder)

    if os.path.exists(sql_output_folder) and not environment_is_dev:
        shutil.rmtree(sql_output_folder)
    ### End clean folders

    ### Create folders structure / blank files
    if not os.path.exists(modalidades_path): 
        os.makedirs(modalidades_path)

    if not os.path.exists(input_file_folder):
        os.makedirs(input_file_folder)
    ### End create folders/files

    #converter()
    #input("Aparte enter para continuar...")
    spliter()
    #input("Aparte enter para continuar...")
    corretor()
    #validator()
    #sqler()
#

print(green("Fim da execução do script..."))