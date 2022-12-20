from bs4 import BeautifulSoup
from slugify import slugify
from Utils.colors import *
from Utils.roman import *
from Utils.lambdas import *
from Utils.numbers import *

def corrector_modality_header(html):
    """ Corretor do estilo do cabeçalho da modalidade """
    title = html.find(lambda tag: is_modalidade_title(tag))
    if title.name != "h3": 
        old_name = title.name
        title.name = "h3"
        print(f"O titulo '{title.string}' foi alterado de {old_name} para h3")
    #
    return html
#

def corrector_topic_title(html):
    """ Corretor do estilo dos titulos dos topicos """
    topics = html.find_all(lambda t: is_topic_title(t))
    print(f"Foram encontrados {bold(len(topics))} topicos")
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
    print(f"Foram arrumados {bold(len(topics))} topicos.")
    return html
#

def corrector_spacing_alphabetic_list_itens(html):
    """ Corretor do espaçamento inicial nas listas alfabeticas """
    letter_list_itens =  html.find_all(name="blockquote")
    print(f"Foram encontrados {bold(len(letter_list_itens))} blockquote")
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
    print(f"Foram removidos {bold(contador_blockquote)} blockquotes.")
    return html
#

def corrector_indentation_alphabetic_lists(html):
    """ Corretor da identação das listas alfabeticas  """
    letter_lists = html.find_all(lambda tag: is_letter_list(tag))
    for letter_list in letter_lists:
        last_list = letter_list.find_previous(name="li")
        if last_list:
            last_list.insert_after(letter_list)
        
        #print("")
    #
    return html
#

def corrector_line_break_alphabetic_lists(html):
    """ Corretor de quebra de linhas em listas alfabeticas """
    letter_lists = html.find_all(lambda tag: is_letter_list(tag))
    for letter_list in letter_lists:
        itens = letter_list.find_all(name="li")
        for item in itens:
            break_line = html.new_tag("br")
            item.p.insert_after(break_line)
        #print("")
    #
    return html
#

def corrector_numbered_lists_after_alphabetic_list(html):
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
    return html
#

def corrector_font_swiss_sans(html):
    # Font em todas as tags
    for tag in html.find_all(): 
        tag['style'] = "font-family: SwissReSans;"
    #

    return html
#

def corrector_marker_nested_lists(html):
    for tag in html.find_all(lambda t: is_letter_list(t)): 
        tag['class'] = "alphabetic_list"
    #
    
    style_tag = html.new_tag("style")
    style_tag.append("ol > li::marker { content: counters(list-item,\".\") \". \"; }")
    style_tag.append("\n")
    style_tag.append('.alphabetic_list > li::marker { content: initial }')
    html.insert(0, style_tag)
    return html
#

def corrector_invalid_characters(html_str):
    html_str.replace(u'\u2013','\u002d')
    return html_str
#

def corrector_converter_nested_list(html):
    list_of_ol = html.find_all('ol', recursive=False)

    def converter_function(ol_item, counter=1, prefix='', type_of_list=''):
        if 'type' in ol_item.attrs: type_of_list = ol_item['type']
        if 'start' in ol_item.attrs: 
            if type_of_list == '1':
                counter = int(ol_item['start'])
            elif type_of_list.lower() == 'a':
                counter = int(letter_to_number(ol_item['start']))
        
        li_list = ol_item.findChildren('li', recursive=False)
        for li_item in li_list:
            primeiro_texto = li_item.find(lambda t: t.name=='p' or t.name=='strong')
            if type_of_list == '1':
                primeiro_texto.string = f"{prefix}{counter}. {primeiro_texto.text}"
            elif type_of_list == 'a':
                letter = number_to_letter(counter)
                primeiro_texto.string = f"{letter}. {primeiro_texto.text}"
            elif type_of_list == 'i':
                letter = toRoman(counter)
                primeiro_texto.string = f"{letter.lower()}. {primeiro_texto.text}"
            #

            filhos = li_item.findChildren('ol', recursive=False)
            for f in filhos: 
                converter_function(f, prefix=f"{prefix}{counter}.")

            counter += 1
        # 
        ol_children_list = ol_item.findChildren('ol', recursive=False)
        for ol_children_item in ol_children_list:
            converter_function(ol_children_item)
        #
    #
    for item in list_of_ol: converter_function(item)

    all_lists = html.find_all('ol')
    for l in all_lists: 
        if 'type' in l.attrs: l['type'] = 'none'
    #
    return html
#
