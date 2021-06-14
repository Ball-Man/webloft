"""Static HTML personal website generator."""
import os.path as pt
import os
import shutil
import glob

from collections import defaultdict

import markdown
import yaml
import django.template as dj_template

TEMPLATES = pt.join(pt.dirname(__file__), 'templates')

# Fields that will be rendered using markdown
# All other fields will be used as plain text
# TODO: maybe transition this list of fields in some template-specific
#       file, so that each template can make small variations if
#       desired.
MD_FIELDS = {'description'}

# Template constants
PROJECT_TEMPLATE_FILE_NAME = '_project.html'
PROJECT_CONFIG_FILE_NAME = 'project.yaml'
PROJECT_DEFAULT_DICT = defaultdict(lambda: 'N/A')


def get_projects(base_dir=pt.curdir):
    """Return the list of projects in the selected base directory.

    A project is identified if it contains a file named
    PROJECT_CONFIG_FILE_NAME.
    """
    return [pt.basename(pt.dirname(file)) for file
            in glob.glob(pt.join(base_dir, '**', '*'))
            if pt.basename(file) == PROJECT_CONFIG_FILE_NAME]


def get_context(base_dir):
    """Retrieve a django-ready context from configuration files.

    A django context is nothing more than a dictionary.
    The given base_dir will be searched for various files and
    directories that will populate the dictionary.

    The final context is hence composed of all the configuration files.

    The first file that will be searched is index.yaml.
    Directories containing a file named PROJECT_CONFIG_FILE_NAME will
    be listed in a subdictionary called 'projects', whose keys are
    the directory names.
    """
    with open(pt.join(base_dir, 'index.yaml')) as file:
        # Load yaml and parse markdown
        context_dic = yaml.safe_load(file)

    # Markdown
    for k in tuple(context_dic.keys()):
        if k in MD_FIELDS:
            context_dic[k] = markdown.markdown(context_dic[k])

    # Projects' subcontexts
    context_dic['projects'] = {}
    for proj_name in get_projects(base_dir):
        with open(pt.join(base_dir, proj_name, PROJECT_CONFIG_FILE_NAME)) \
                as file:
            context_dic['projects'][proj_name] = yaml.safe_load(file)

    # Markdown for project files
    for projects in context_dic['projects'].values():
        for k in tuple(projects.keys()):
            if k in MD_FIELDS:
                projects[k] = markdown.markdown(projects[k])

    return dj_template.Context(context_dic)


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


def render_project(context, project_name, template_name='aquarius'):
    """Render a template in a string, by project name.

    Internally, it uses the render function to render a specific file,
    but preliminary actions are made in order to render the correct
    project data.
    """
    context['project'] = context['projects'][project_name]

    ret = render(context, PROJECT_TEMPLATE_FILE_NAME, template_name)

    context['project'] = PROJECT_DEFAULT_DICT
    return ret


def build(base_dir=pt.curdir, template_name='null', dist_dir='dist',
          templated_exts=('.html',)):
    """Render and save an entire template, given the base dir.

    The dist_dir can be specified, and will contain the HTML files (and
    images) ready to be deployed.

    Template files starting with '_' will be omitted. This makes it
    possible to use base templates, which is a common practice in the
    django templating workflow.
    """
    abs_template_files = glob.glob(pt.join(TEMPLATES, template_name, '**',
                                           '*'),
                                   recursive=True)
    template_files = (pt.relpath(path, pt.join(TEMPLATES, template_name))
                      for path in abs_template_files)

    # Create dist directory
    abs_dist_dir = pt.join(base_dir, dist_dir)
    mkdir_safe(abs_dist_dir)

    # Generated build
    context = get_context(base_dir)
    for abs_file, file in zip(abs_template_files, template_files):
        dest = pt.join(abs_dist_dir, file)

        if pt.isdir(abs_file):
            os.mkdir(dest)
        elif pt.isfile(abs_file) \
             and pt.splitext(file)[1].lower() in templated_exts:
            if pt.basename(file)[0] != '_':
                with open(dest, 'w') as fout:
                    fout.write(render(context, file,
                               template_name))
        elif pt.isfile(abs_file) and pt.basename(file)[0] != '_':
            shutil.copy(abs_file, dest)

    # Build project files
    for proj_name, proj in context['projects'].items():
        mkdir_safe(pt.join(base_dir, dist_dir, proj_name))


def mkdir_safe(dirname):
    """Make the given directory if it doesn't exist.

    Ignore otherwise.
    """
    if not pt.isdir(dirname):
        os.mkdir(dirname)
