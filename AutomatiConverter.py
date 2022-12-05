from bs4 import BeautifulSoup
from slugify import slugify
from Utils.colors import colors
import os

# https://pandoc.org/try/
# https://www.uv.es/wikibase/doc/cas/pandoc_manual_2.7.3.wiki


## Parametrização
input_file              = "DOCX/75_29-11.docx"
output_path             = "HTML"
output_full_html_file   = f"{output_path}/output_full.html"
modalidades_path        = f"{output_path}/Modalidades"
modalidade_prefix       = "Modalidade_id_"
## End Parametrização

## -------------------------------
## Etapa de Conversão


def converter():
    print(":::::::::::::::::::::::::")
    print("Iniciando conversão via pandoc...")
    print(f"Arquivo de entrada: {colors.underline(input_file)}")
    print(colors.yellow("Executando o comando..."))
    print(colors.bold(f"pandoc --from docx --to html5 --no-highlight -o {output_full_html_file} {input_file}"))
    os.system(f"pandoc --from docx --to html5 --no-highlight -o {output_full_html_file} {input_file}")
    print(colors.green("Comando executado com sucesso"))
    print(f"Gerado o arquivo {colors.underline(output_full_html_file)}")
#

def spliter():
    print("Iniciando a etapa de Split...")
    with open(output_full_html_file, "r", encoding='utf-8') as html_file:
        html_doc = html_file.read()
        html_file.close()
    #

    parsed_html = BeautifulSoup(html_doc, 'html.parser')
    print(colors.green(f"Parserizado o arquivo {output_full_html_file}"))

    def find_modalidades(tag): 
        is_strong = (tag.name == "strong")
        is_mod_captalize_case = ('Modalidade' in tag.text)
        is_mod_upper_case = ('MODALIDADE' in tag.text)

        return is_strong and (is_mod_captalize_case or is_mod_upper_case)
    #

    modalidades = parsed_html.find_all(lambda tag: find_modalidades(tag))

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
    print("Iniciando o modulo de correção")
    modalidades_files = os.listdir(modalidades_path)
    print(f"Foram encontrados {colors.bold(len(modalidades_files))} arquivos de modalidade")
    for index,modalidade_file_name in enumerate(modalidades_files):
        with open(f"{modalidades_path}/{modalidade_file_name}", "r") as modalidade:
            modalidade_html = modalidade.read()
            modalidade.close()
        #
        print(colors.blue(f"{index} - {modalidade_file_name}"))
        parsed_modalidade = BeautifulSoup(modalidade_html, 'lxml')
        title = parsed_modalidade.strong
        if title.find_parent().name == "h1":
            print("Titulo bugado")
        #
        

    #
#

## -------------------------------

#converter()
#spliter()
corretor()

### Modulo de inspeção?
