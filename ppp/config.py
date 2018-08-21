"""Configuration settings for PPP package."""

from jinja2 import Environment, PackageLoader
import re

def question_number(question_number, max_length = 4):
    """Splitting question number.

    Splitting string first by separator chars, then separating
    letters from numbers, and then splitting just by length.
    All actions performed one-by-one and only if needed.

    Args:
        question_number: Question number in a string representation.
        max_length: Max length of each chunk, with a default value = 4.
        
    Returns:
        Original question number, splitted to (=< max_lengh) chunks
        and then joined to one string with a space char as a glue.
    """
  # If question's length is less then limit, return immediately.
  if len(question_number) <= max_length:
    return question_number
  
  # Split question number by separator chars.
  while True:
    pieces = re.split("[^A-Za-z0-9 ]", question_number, 1)
    if len(pieces) == 1:
      break
    elif len(pieces[1]) > max_length:
      question_number = ' '.join(pieces)
      continue
    else:
      break
  
  # If string chunk is longer then limit, split numbers from letters in it.    
  pieces = (' '.join(pieces)).split(' ')
  for index, value in enumerate(pieces):
    if len(value) > max_length:
      pieces[index] = ' '.join(map(str.strip, re.findall('(\d+|\D+)', value)))
  
  # If string chunk is still longer then limit, split it by limit chars.    
  pieces = (' '.join(pieces)).split(' ')
  for index, value in enumerate(pieces):
    if len(value) > max_length:
      pieces[index] = ' '.join([value[i:i+max_length] for i in range(0, len(value), max_length)])
  
  return ' '.join(pieces)
    
def get_template_env(template):
  ENV = Environment(loader=PackageLoader('ppp', 'templates/' + template), trim_blocks=True, lstrip_blocks=True)
  ENV.filters['question_number'] = question_number
  return ENV
  
EXCLUSION_TOKEN = 'X'
