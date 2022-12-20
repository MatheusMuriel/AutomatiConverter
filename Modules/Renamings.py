import csv

def prepare_list_of_renamings(csv_file):
    with open(csv_file, 'r', encoding='utf8') as read_obj:
    
        # Return a reader object which will
        # iterate over lines in the given csvfile
        csv_reader = csv.reader(read_obj, delimiter=";")
    
        # convert string to list
        return list(csv_reader)
    #
#

def get_renamed_title_for(original_title, renamings_list: list[list[str]]):
    """ Obter o novo título para a seção com base no arquivo CSV especificado """

    for current_title in renamings_list:
        if current_title[0] == original_title:
            return current_title[1]
        #
    #
    
    return original_title
#