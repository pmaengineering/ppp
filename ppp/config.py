"""Configuration settings for PPP package."""

from jinja2 import Environment, PackageLoader

def question_number(s):
    return ' '.join([s[i:i + 4] for i in range(0, len(s), 4)])
    
def get_template_env(template):
  ENV = Environment(loader=PackageLoader('ppp', 'templates/' + template), trim_blocks=True, lstrip_blocks=True)
  ENV.filters['question_number'] = question_number
  return ENV
  
EXCLUSION_TOKEN = 'X'
