def is_modalidade_title(tag): 
    is_strong = (tag.name == "strong" or tag.name == "h3")
    is_mod_captalize_case = ('Modalidade' in tag.text)
    is_mod_upper_case = ('MODALIDADE' in tag.text)

    return is_strong and (is_mod_captalize_case or is_mod_upper_case)
#

def is_letter_list(tag):
    is_list = (tag.name == "ol")
    is_type_a = False
    is_type_i = False
    if ('type' in tag.attrs):
        is_type_a = (tag['type'] == "a")
        is_type_i = (tag['type'] == "i")

    return is_list and (is_type_a or is_type_i)
#

def is_numeric_list(tag):
    is_list = (tag.name == "ol")
    is_type_1 = False
    if ('type' in tag.attrs):
        is_type_1 = (tag['type'] == "1")

    return is_list and (is_type_1)
#

def is_topic_title(tag):
    #topics = html.find_all('h1', {'id': re.compile(r'.+')})
    have_id = ('id' in tag.attrs)

    return have_id
#

def is_alphabetic_or_roman_list_with_numbered_after(tag):
    is_a_letter_list = is_letter_list(tag)

    if is_a_letter_list:
        numeric_list_childrens = tag.findChildren(lambda t: is_numeric_list(t))
        if numeric_list_childrens:
            return True
        else:
            return False
    else:
        return False
#
