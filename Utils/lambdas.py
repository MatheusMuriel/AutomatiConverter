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
    
