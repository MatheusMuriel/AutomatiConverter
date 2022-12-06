from bs4 import BeautifulSoup
from slugify import slugify
from Utils.colors import colors
from Utils.numeros_romanos import romanToDecimal
from Utils.lambdas import is_modalidade_title
import os
import re

# Referencias e Documentações
# https://pandoc.org/try/
# https://www.uv.es/wikibase/doc/cas/pandoc_manual_2.7.3.wiki
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/

## Parametrização
input_file              = "DOCX/75_29-11.docx"
output_path             = "HTML"
output_full_html_file   = f"{output_path}/output_full.html"
modalidades_path        = f"{output_path}/Modalidades"
modalidade_prefix       = "Modalidade_id_"
## End Parametrização

def converter():
    print(colors.bold(":::::::::::::::::::::::::"))
    print("Iniciando conversão via pandoc...")
    print(f"Arquivo de entrada: {colors.underline(input_file)}")
    print(colors.yellow("Executando o comando..."))
    print(colors.bold(f"pandoc --from docx --to html5 --no-highlight -o {output_full_html_file} {input_file}"))
    os.system(f"pandoc --from docx --to html5 --no-highlight -o {output_full_html_file} {input_file}")
    print(colors.green("Comando executado com sucesso"))
    print(f"Gerado o arquivo {colors.underline(output_full_html_file)}")
#

def spliter():
    print(colors.bold(":::::::::::::::::::::::::"))
    print("Iniciando a etapa de Split...")
    with open(output_full_html_file, "r", encoding='utf-8') as html_file:
        html_doc = html_file.read()
        html_file.close()
    #

    parsed_html = BeautifulSoup(html_doc, 'html.parser')
    print(colors.green(f"Parserizado o arquivo {output_full_html_file}"))

    modalidades = parsed_html.find_all(lambda tag: is_modalidade_title(tag))

    for m in modalidades[1:]:
        m.parent.insert_before("###DIVIDER###")
    #

    str_html = str(parsed_html)
    pages = str_html.split("###DIVIDER###")
    print(f"Dividido em {colors.bold(len(pages))} partes")

    print(colors.yellow("Salvando arquivos..."))
    for index,page in enumerate(pages):
        parsed_page = BeautifulSoup(page, 'html.parser')
        file_name = f"{index}_{slugify(parsed_page.strong.text)}.html"
        with open(f"{modalidades_path}/{file_name}", 'w') as html_file:
            html_file.write(page)
        #
    #
    print(colors.green("Arquivos salvos."))
#

def corretor():
    print(colors.bold(":::::::::::::::::::::::::"))
    print("Iniciando o modulo de correção")
    modalidades_files = os.listdir(modalidades_path)
    print(f"Foram encontrados {colors.bold(len(modalidades_files))} arquivos de modalidade")
    for index,modalidade_file_name in enumerate(modalidades_files):
        modalidade = open(f"{modalidades_path}/{modalidade_file_name}", "r+")
        modalidade_html = modalidade.read()
        modalidade.close()
        
        print(colors.blue(f"{index} - {modalidade_file_name}"))
        #html = BeautifulSoup(modalidade_html, 'lxml')
        html = BeautifulSoup(modalidade_html, 'html.parser')
        # TODO ver pq ta colocando HTML

        title = html.find(lambda tag: is_modalidade_title(tag))
        
        if title.name != "h3": 
            title.string = title.string.replace('\n',' ')
            #print(f"O titulo '{title.string}' foi alterado de {title.name} para h3")
            title.name = "h3"
        #

        topics = html.find_all('h1', {'id': re.compile(r'.+')})
        print(f"Foram encontrados {len(topics)} topicos")
        for topic in topics:
            if topic.findChildren():
                #print("Tem coisa dentro")
                text = topic.text.replace('\n',' ')
                for child in topic.findChildren(): 
                    child.extract()
                topic.string = text
            if topic.name != "strong":  
                print(f"O topico '{topic.string}' foi alterado de {topic.name} para strong")
                topic.name = "strong"
            #
        #

        letter_list_itens =  html.find_all(name="blockquote")
        print(f"Foram encontrados {len(letter_list_itens)} blockquote")
        for blockquote in letter_list_itens:
            if blockquote.findChild():
                sub_tag = blockquote.findChild()
                super_tag = blockquote.find_parent()
                blockquote.extract()
                super_tag.insert(0, sub_tag)
            #
        #
        
        modalidade = open(f"{modalidades_path}/{modalidade_file_name}", "w")
        #modalidade = open(f"{modalidades_path}/alt_{modalidade_file_name}", "w")
        modalidade.write(str(html))
        modalidade.close()
    #
#

def sqler():
    print(colors.bold(":::::::::::::::::::::::::"))
    print("Iniciando o modulo de SQL")
    modalidades_files = os.listdir(modalidades_path)
    print(f"Foram encontrados {colors.bold(len(modalidades_files))} arquivos de modalidade")
    
    for index,modalidade_file_name in enumerate(modalidades_files):
        with open(f"{modalidades_path}/{modalidade_file_name}", "r") as modalidade:
            modalidade_html = modalidade.read()
            modalidade.close()
        #
        roman_number_regex = "-M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})-"
        search_result = re.search(roman_number_regex, modalidade_file_name.upper())
        if search_result is not None:
            roman_number = search_result.group().replace("-","")
            modalite_number = romanToDecimal(roman_number)
            print(modalite_number)
        else:
            print(colors.red(f"Numero romano não encontrado no arquivo: {modalidade_file_name}"))
        #

        #print(colors.blue(f"{index} - {modalidade_file_name}"))
        #parsed_modalidade = BeautifulSoup(modalidade_html, 'lxml')
        #title = parsed_modalidade.strong.text
        #print(title)
    #
#

## -------------------------------

#converter()
spliter()
corretor()
#sqler()

### Modulo de inspeção?
### Modulo SQL
