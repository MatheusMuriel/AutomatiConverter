def is_modalidade_title(tag): 
    is_strong = (tag.name == "strong")
    is_mod_captalize_case = ('Modalidade' in tag.text)
    is_mod_upper_case = ('MODALIDADE' in tag.text)

    return is_strong and (is_mod_captalize_case or is_mod_upper_case)
#