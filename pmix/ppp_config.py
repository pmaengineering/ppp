from jinja2 import Environment, PackageLoader


template_env = Environment(loader=PackageLoader('pmix'), trim_blocks=True, lstrip_blocks=True)
