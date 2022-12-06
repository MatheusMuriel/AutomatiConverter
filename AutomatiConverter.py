from bs4 import BeautifulSoup
from slugify import slugify
from Utils.colors import colors
from Utils.numeros_romanos import romanToDecimal
from Utils.lambdas import is_modalidade_title
from Utils.lambdas import is_letter_list
import os
import re

# Referencias e Documentações
# https://pandoc.org/try/
# https://www.uv.es/wikibase/doc/cas/pandoc_manual_2.7.3.wiki
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/

## Parametrização
input_file               = "DOCX/75_29-11.docx"
output_path              = "HTML"
output_full_html_file    = f"{output_path}/output_full.html"
output_parcial_html_file = f"{output_path}/output_parcial.html"
modalidades_path         = f"{output_path}/Modalidades"
modalidade_prefix        = "Modalidade_id_"
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
    
    # TODO temporariamente como parcial
    with open(output_parcial_html_file, "r", encoding='utf-8') as html_file:
    #with open(output_full_html_file, "r", encoding='utf-8') as html_file:
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
    str_html = str_html.replace('\n',' ')
    pages = str_html.split("###DIVIDER###")
    print(f"Dividido em {colors.bold(len(pages))} partes")

    print(colors.yellow("Salvando arquivos..."))
    for index,page in enumerate(pages):
        parsed_page = BeautifulSoup(page, 'html.parser')
        file_name = f"{slugify(parsed_page.strong.text)}.html"
        #file_name = f"{index}_{slugify(parsed_page.strong.text)}.html"
        with open(f"{modalidades_path}/{file_name}", 'w') as html_file:
            html_file.write(page)
        #
    #
    print(colors.green("Arquivos salvos."))
#

def corretor():
    print(colors.bold(":::::::::::::::::::::::::"))
    print("Iniciando o etapa de Correção...")
    modalidades_files = os.listdir(modalidades_path)
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
            #print(f"O titulo '{title.string}' foi alterado de {old_name} para h3")
        #
        """ ... """

        """ Corretor do estilo dos titulos dos topicos """
        topics = html.find_all('h1', {'id': re.compile(r'.+')})
        #print(f"Foram encontrados {colors.bold(len(topics))} topicos")
        for topic in topics:
            if topic.findChildren():
                # Tratativa para evitar o strong dentro de strong
                text = topic.text.replace('\n',' ')
                for child in topic.findChildren(): 
                    child.extract()
                topic.string = text
            if topic.name != "strong":  
                #print(f"O topico '{topic.string}' foi alterado de {topic.name} para strong")
                topic.name = "strong"
            #
        #
        print(f"Foram arrumados {colors.bold(len(topics))} topicos.")

        """ Corretor do espaçamento inicial nas listas alfabeticas """
        letter_list_itens =  html.find_all(name="blockquote")
        #print(f"Foram encontrados {colors.bold(len(letter_list_itens))} blockquote")
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
        #letter_lists = html.find_all(lambda tag: is_letter_list(tag))
        #for letter_list in letter_lists:
            #last_list = letter_list.find_previous(name="li")
            #if last_list:
                #last_list.insert_after(letter_list)
            #
            #print("")
        #

        """ Corretor de quebra de linhas em listas alfabeticas """
        letter_lists = html.find_all(lambda tag: is_letter_list(tag))
        for letter_list in letter_lists:
            itens = letter_list.find_all(name="li")
            for item in itens:
                break_line = html.new_tag("br")
                item.p.insert_after(break_line)
            #print("")
        #

        
        # Font em todas as tags
        for tag in html.find_all(): tag['style'] = "font-family: SwissReSans;"

        spam_geral = html.new_tag("span")
        #spam_geral['style'] = "font-family: SwissReSans !important;"
        spam_geral.insert(0, html)

        print(colors.yellow("Salvando arquivo..."))
        modalidade = open(f"{modalidades_path}/{modalidade_file_name}", "w")
        #modalidade = open(f"{modalidades_path}/alt_{modalidade_file_name}", "w")
        modalidade.write(str(spam_geral))
        modalidade.close()
        print(colors.green("Arquivo salvo."))
    #
    print(colors.green("Fim da etapa de Correção."))
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
