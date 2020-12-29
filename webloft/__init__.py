"""Static HTML personal website generator."""
import os.path as pt

import yaml
import django.template as dj_template

TEMPLATES = pt.join(pt.dirname(__file__), 'templates')


def get_context(base_dir):
    """Retrieve a django-ready context from configuration files.

    A django context is nothing more than a dictionary.
    The given base_dir will be searched for various files and
    directories that will populate the dictionary.

    The final context is hence composed of all the configuration files.

    The first file that will be searched is index.yaml.
    """
    with open(pt.join(base_dir, 'index.yaml')) as file:
        return dj_template.Context(yaml.load(file))


def render(context, file='index.html', template_name='aquarius'):
    """Render a template in a string, by file.

    A webloft template is often much more than a file. Each file is a
    django template. Rendering all the files in the template directory
    gives a full render of the website.

    The template name is searched in the directory specified by
    TEMPLATES. The file name is searched in the directory composed by:
    TEMPLATES/template_name
    """
    engine = dj_template.Engine(dirs=[pt.join(TEMPLATES, template_name)])
    template = engine.get_template(file)
    return template.render(context)
