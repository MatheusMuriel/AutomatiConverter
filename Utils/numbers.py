import string

def number_to_letter(num):
  return string.ascii_lowercase[num-1]

def letter_to_number(letter):
  return string.ascii_lowercase.index(letter)+1