import string

def number_to_letter(num):
  is_overflowed = False
  num_of_overflow = 0 
  if num > 26:
    num_of_overflow = num // 26
    is_overflowed = True
    num = num - (num_of_overflow * 26)
  letter = string.ascii_lowercase[num-1]

  if not is_overflowed:
    return letter
  else:
    return f"{string.ascii_lowercase[num_of_overflow-1]}{letter}"
  #
#

def letter_to_number(letter):
  return string.ascii_lowercase.index(letter)+1
#