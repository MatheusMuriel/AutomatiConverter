import os
import re
import sys
import webbrowser
from bs4 import BeautifulSoup
from slugify import slugify
from Utils.colors import colors
from Utils.numeros_romanos import romanToDecimal
from Utils.lambdas import is_modalidade_title
from Utils.lambdas import is_letter_list
from Utils.lambdas import is_numeric_list
from Utils.lambdas import is_topic_title
from Utils.lambdas import is_alphabetic_or_roman_list_with_numbered_after


# Referencias e Documentações
# https://pandoc.org/try/
# https://www.uv.es/wikibase/doc/cas/pandoc_manual_2.7.3.wiki
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/

## Parametrização
#input_file          = "DOCX/75_29-11.docx"
input_file          = "DOCX/76_05-12.docx"
#input_file          = "DOCX/04-76_05-12.docx"

html_output_folder  = "HTML"
html_output_file    = f"{html_output_folder}/output_full.html"
modalidades_path    = f"{html_output_folder}/Modalidades"

sql_output_folder   = "SQL"
sql_output_file     = f"{sql_output_folder}/output.sql"


ramo                      = "75"
category_code_start       = 92
modality_order_code_start = 14
## End Parametrização

def converter():
    print(colors.bold(":::::::::::::::::::::::::"))
    print("Iniciando conversão via pandoc...")
    print(f"Arquivo de entrada: {colors.underline(input_file)}")
    print(colors.yellow("Executando o comando..."))
    print(colors.bold(f"pandoc --from docx --to html5 --no-highlight -o {html_output_file} {input_file}"))
    os.system(f"pandoc --from docx --to html5 --no-highlight -o {html_output_file} {input_file}")
    print(colors.green("Comando executado com sucesso"))
    print(f"Gerado o arquivo {colors.underline(html_output_file)}")
#

def spliter():
    print(colors.bold(":::::::::::::::::::::::::"))
    print("Iniciando a etapa de Split...")
    
    with open(html_output_file, "r", encoding='utf-8') as html_file:
        html_doc = html_file.read()
        html_file.close()
    #

    parsed_html = BeautifulSoup(html_doc, 'html.parser')
    print(colors.green(f"Parserizado o arquivo {html_output_file}"))

    modalidades = parsed_html.find_all(lambda tag: is_modalidade_title(tag))

    for m in modalidades[1:]:
        m.parent.insert_before("###DIVIDER###")
    #

    str_html = str(parsed_html)
    str_html = str_html.replace('\n',' ')
    pages = str_html.split("###DIVIDER###")
    print(f"Dividido em {colors.bold(len(pages))} partes")

    print(colors.yellow("Salvando arquivos..."))
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
            print(colors.red(f"Numero romano não encontrado no arquivo: {title.text}"))
            #file_name = f"{slugify(title.text)}.html"
        #file_name = f"{index}_{slugify(title.text)}.html"
        #with open(f"{modalidades_path}/{file_name}", 'w') as html_file:
            #html_file.write(page)
        #
    #
    print(colors.green("Arquivos salvos."))
#

def corretor():
    print(colors.bold(":::::::::::::::::::::::::"))
    print("Iniciando o etapa de Correção...")
    modalidades_files = os.listdir(modalidades_path)
    if '.gitkeep' in modalidades_files: 
        modalidades_files.remove('.gitkeep')
    
    print(f"Foram encontrados {colors.bold(len(modalidades_files))} arquivos de modalidade")
    for index,modalidade_file_name in enumerate(modalidades_files):
        modalidade = open(f"{modalidades_path}/{modalidade_file_name}", "r+")
        modalidade_html = modalidade.read()
        modalidade.close()
        
        print(colors.blue(f"{index+1} - {modalidade_file_name}"))
        html = BeautifulSoup(modalidade_html, 'html.parser')
        
        """ Corretor do estilo do cabeçalho da modalidade """
        title = html.find(lambda tag: is_modalidade_title(tag))
        if title.name != "h3": 
            old_name = title.name
            title.name = "h3"
            print(f"O titulo '{title.string}' foi alterado de {old_name} para h3")
        #
        """ ... """

        """ Corretor do estilo dos titulos dos topicos """
        topics = html.find_all(lambda t: is_topic_title(t))
        print(f"Foram encontrados {colors.bold(len(topics))} topicos")
        for topic in topics:
            if topic.findChildren():
                # Tratativa para evitar o strong dentro de strong
                text = topic.text.replace('\n',' ')
                for child in topic.findChildren(): 
                    child.extract()
                topic.string = text
            if topic.name != "strong":  
                print(f"O topico '{topic.string}' foi alterado de {topic.name} para strong")
                topic.name = "strong"
            #
        #
        print(f"Foram arrumados {colors.bold(len(topics))} topicos.")

        """ Corretor do espaçamento inicial nas listas alfabeticas """
        letter_list_itens =  html.find_all(name="blockquote")
        print(f"Foram encontrados {colors.bold(len(letter_list_itens))} blockquote")
        contador_blockquote = 0
        for blockquote in letter_list_itens:
            if blockquote.findChild():
                sub_tag = blockquote.findChild()
                super_tag = blockquote.find_parent()
                if super_tag.name == "li":
                    blockquote.extract()
                    super_tag.insert(0, sub_tag)
                else:
                    blockquote.name = "p"
                contador_blockquote += 1
            #
        #
        print(f"Foram removidos {colors.bold(contador_blockquote)} blockquotes.")

        """ Corretor da identação das listas alfabeticas  """
        letter_lists = html.find_all(lambda tag: is_letter_list(tag))
        for letter_list in letter_lists:
            last_list = letter_list.find_previous(name="li")
            if last_list:
                last_list.insert_after(letter_list)
            
            #print("")
        #

        """ Corretor de quebra de linhas em listas alfabeticas """
        letter_lists = html.find_all(lambda tag: is_letter_list(tag))
        for letter_list in letter_lists:
            itens = letter_list.find_all(name="li")
            for item in itens:
                break_line = html.new_tag("br")
                #item.p.insert_after(break_line)
            #print("")
        #

        # TODO - Ver o negocio do 3.1, 3.2
        # TODO - Ver as sublistas 

        """ Corretor das listas numeradas após listas alfabeticas """
        letter_with_num_lists = html.find_all(lambda t: is_alphabetic_or_roman_list_with_numbered_after(t))
        for letter_list in letter_with_num_lists:
            numeric_lists = letter_list.findChildren(lambda t: is_numeric_list(t))
            numeric_lists.reverse()
            for numeric_list in numeric_lists:
                numeric_itens = numeric_list.find_all("li")
                if numeric_itens:
                    numeric_itens.reverse()
                    for numeric_item in numeric_itens:
                        letter_list.insert_after(numeric_item)
        ####
        
        """ Corretor da fonte, estilo, caracteres e span """
        # Font em todas as tags
        for tag in html.find_all(): tag['style'] = "font-family: SwissReSans;"
        style_tag = html.new_tag("style")
        #style_tag.append("ol > li::marker { content: counters(list-item,\". \") \". \"; }")
        #html.insert(0, style_tag)

        #spam_geral = html.new_tag("span")
        #spam_geral['style'] = "font-family: SwissReSans !important;"
        #spam_geral.insert(0, html)

        spam_geral = html
        output_html = str(spam_geral)
        output_html = output_html.replace(u'\u2013','\u002d')
        """ .... """

        print(colors.yellow("Salvando arquivo..."))
        modalidade = open(f"{modalidades_path}/{modalidade_file_name}", "w")
        modalidade.write(output_html)
        modalidade.close()
        print(colors.green("Arquivo salvo."))
    #
    print(colors.green("Fim da etapa de Correção."))
#

def sqler():
    input("Verifique os arquivos html e se estiver certo aparte enter para continuar com o modulo SQLer...")
    print(colors.bold(":::::::::::::::::::::::::"))
    print("Iniciando o modulo de SQL")
    modalidades_files = os.listdir(modalidades_path)
    if '.gitkeep' in modalidades_files: 
        modalidades_files.remove('.gitkeep')
    print(f"Foram encontrados {colors.bold(len(modalidades_files))} arquivos de modalidade")

    category_code = category_code_start
    modality_order_code = modality_order_code_start

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
    print(colors.bold(":::::::::::::::::::::::::"))
    print("Iniciando o modulo Validator")
    modalidades_files = os.listdir(modalidades_path)
    print(f"Foram encontrados {colors.bold(len(modalidades_files))} arquivos de modalidade")
    pwd = os.getcwd()
    pwd = pwd.replace("\\", "/")
    url_file_list = f"file:///{pwd}/{modalidades_path}"
    _url_file_list = f"{pwd}/{modalidades_path}"
    print(url_file_list)
    webbrowser.open(f"file:{_url_file_list}")
#
## -------------------------------
#converter()
#input("Aparte enter para continuar...")
#spliter()
#input("Aparte enter para continuar...")
#corretor()
validator()
#sqler()

print(colors.green("Fim da execução do script..."))