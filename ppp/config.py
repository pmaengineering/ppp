"""Configuration settings for PPP package."""

from jinja2 import Environment, PackageLoader


def get_template_env(template):
  return Environment(loader=PackageLoader('ppp', 'templates/' + template), trim_blocks=True, lstrip_blocks=True)

EXCLUSION_TOKEN = 'X'
