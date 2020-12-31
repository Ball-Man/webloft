"""Static HTML personal website generator."""
import os.path as pt
import os
import shutil
import glob

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


def build(base_dir=pt.curdir, template_name='aquarius', dist_dir='dist',
          templated_exts=('.html',)):
    """Render and save an entire template, given the base dir.

    The dist_dir can be specified, and will contain the HTML files (and
    images) ready to be deployed.

    Template files starting with '_' will be omitted. This makes it
    possible to use base templates, which is a common practice in the
    django templating workflow.
    """
    abs_template_files = glob.glob(pt.join(TEMPLATES, template_name, '**', '*'),
                                   recursive=True)
    template_files = (pt.relpath(path, pt.join(TEMPLATES, template_name))
                      for path in abs_template_files)

    # Create dist directory
    abs_dist_dir = pt.join(base_dir, dist_dir)
    if not pt.isdir(abs_dist_dir):
        os.mkdir(abs_dist_dir)

    # Generated build
    for abs_file, file in zip(abs_template_files, template_files):
        dest = pt.join(abs_dist_dir, file)

        if pt.isdir(abs_file):
            os.mkdir(dest)
        elif pt.isfile(abs_file) \
             and pt.splitext(file)[1].lower() in templated_exts:
            if pt.basename(file)[0] != '_':
                with open(dest, 'w') as fout:
                    fout.write(render(get_context(base_dir), file,
                               template_name))
        elif pt.isfile(abs_file):
            shutil.copy(abs_file, dest)
