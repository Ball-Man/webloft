"""Static HTML personal website generator."""
import os.path as pt
import os
import shutil
import glob
import logging
import copy
import functools

from collections import defaultdict

import markdown
import yaml
import django.template as dj_template

TEMPLATES = pt.join(pt.dirname(__file__), 'templates')
GLOBAL_DEFAULTS_FILE = pt.join(TEMPLATES, 'defaults.yaml')
TEMPLATE_DEFAULTS_FILE_NAME = '_defaults.yaml'

# Fields that will be rendered using markdown
# All other fields will be used as plain text
# TODO: maybe transition this list of fields in some template-specific
#       file, so that each template can make small variations if
#       desired.
MD_FIELDS = {'description'}

# Template constants
PROJECT_TEMPLATE_FILE_NAME = '_project.html'
PROJECT_CONFIG_FILE_NAME = 'project.yaml'

# Callable, preferable to the simple markdown.markdown since it
# encapsules all the extensions used.
MARKDOWN_PARTIAL = functools.partial(markdown.markdown,
                                     extensions=['fenced_code'])


def get_projects(base_dir=pt.curdir):
    """Return the list of projects in the selected base directory.

    A project is identified if it contains a file named
    PROJECT_CONFIG_FILE_NAME.
    """
    return [pt.basename(pt.dirname(file)) for file
            in glob.glob(pt.join(base_dir, '**', '*'))
            if pt.basename(file) == PROJECT_CONFIG_FILE_NAME]


def get_defaults(template_name=None):
    """Return a pair of dictionaries with default values for contexts.

    The return format is (index_defaults, project_defaults).
    """
    # Retrieve global defaults
    with open(GLOBAL_DEFAULTS_FILE) as file:
        defaults = yaml.safe_load(file)

    index_defaults = defaults['index']
    project_defaults = defaults['project']

    if template_name is None:
        return index_defaults, project_defaults

    # Update with template specific defaults
    template_default_file = pt.join(TEMPLATES, template_name,
                                    TEMPLATE_DEFAULTS_FILE_NAME)

    # If no file is given, return the globals
    if not pt.isfile(template_default_file):
        return index_defaults, project_defaults

    with open(template_default_file) as file:
        template_defaults = yaml.safe_load(file)

    index_defaults.update(template_defaults.get('index', {}))
    project_defaults.update(template_defaults.get('project', {}))

    return index_defaults, project_defaults


def get_context(base_dir, template_name):
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
        # Load yaml
        user_context_dic = yaml.safe_load(file) or {}

    # Optionally load description from file
    if user_context_dic.get('description_file') is not None:
        user_context_dic['description'] = open(
            pt.join(base_dir, user_context_dic['description_file'])).read()

    # Markdown
    for k in tuple(user_context_dic.keys()):
        if k in MD_FIELDS:
            user_context_dic[k] = MARKDOWN_PARTIAL(user_context_dic[k])

    # Use defaults
    context_dic, proj_dict_default = get_defaults(template_name)
    context_dic.update(user_context_dic)

    # Projects' subcontexts
    context_dic['projects'] = {}
    for proj_name in get_projects(base_dir):
        with open(pt.join(base_dir, proj_name, PROJECT_CONFIG_FILE_NAME)) \
                as file:
            user_dict = yaml.safe_load(file) or {}

        # Copy default dictionary and update with user data
        proj_dict = copy.deepcopy(proj_dict_default)
        # Inspect files
        # Update extensions with user preferences before inspecting
        if 'image_types' in user_dict:
            proj_dict['image_types'] = user_dict['image_types']

        proj_dir = pt.join(base_dir, proj_name)
        proj_files = [pt.relpath(file, start=proj_dir) for file in
                      glob.glob(pt.join(proj_dir, '*'))
                      if not is_ignored(file) and not pt.isdir(file)
                         and pt.basename(file) != PROJECT_CONFIG_FILE_NAME]
        proj_dict['project_files'] = proj_files
        # Update project files before computing the gallery
        if 'project_files' in user_dict:
            proj_dict['project_files'] = user_dict['project_files']
        proj_dict['gallery_images'] = [
            file for file in proj_files
            if str.lower(pt.splitext(file)[1]) in proj_dict['image_types']]

        # Optionally load description from file
        if user_dict.get('description_file') is not None:
            user_dict['description'] = open(
                pt.join(proj_dir, user_dict['description_file'])).read()

        context_dic['projects'][proj_name] = proj_dict
        context_dic['projects'][proj_name].update(user_dict)

        logging.debug(f'project: {proj_name}')
        logging.debug(f'project directory: {proj_dir}')
        logging.debug(f"project files: {proj_dict['project_files']}")
        logging.debug(f"project image types: {proj_dict['image_types']}")
        logging.debug(f"project gallery: {proj_dict['gallery_images']}")

    # Markdown for project files
    for projects in context_dic['projects'].values():
        for k in tuple(projects.keys()):
            if k in MD_FIELDS:
                projects[k] = MARKDOWN_PARTIAL(projects[k])

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

    context['project'] = None
    return ret


def build(base_dir=pt.curdir, template_name='aquarius', dist_dir='dist',
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
    context = get_context(base_dir, template_name)
    for abs_file, file in zip(abs_template_files, template_files):
        dest = pt.join(abs_dist_dir, file)

        if pt.isdir(abs_file):
            os.mkdir(dest)
        elif pt.isfile(abs_file) \
             and pt.splitext(file)[1].lower() in templated_exts:
            if not is_ignored(file):
                with open(dest, 'w') as fout:
                    fout.write(render(context, file,
                               template_name))
        elif pt.isfile(abs_file) and not is_ignored(file):
            shutil.copy(abs_file, dest)

    # Copy logo
    if context['logo'] is not None and pt.isfile(
            logo := pt.join(base_dir, context['logo'])):
        shutil.copy(logo, abs_dist_dir)
        logging.debug(f"found logo: {context['logo']}")

    # Build project files
    for proj_name, proj in context['projects'].items():
        proj_dist_dir = pt.join(base_dir, dist_dir, proj_name)
        proj_dir = pt.join(base_dir, proj_name)
        mkdir_safe(proj_dist_dir)

        # Main project page
        with open(pt.join(proj_dist_dir, 'index.html'), 'w') as fout:
            fout.write(render_project(context, proj_name, template_name))

        # Copy project files
        # Directories and ignored files will not be copied
        for file in proj['project_files']:
            shutil.copy(pt.join(proj_dir, file), proj_dist_dir)


def delete(base_dir=pt.curdir, dist_dir='dist'):
    """Delete the dist directory and exit."""
    dist_dir_path = pt.join(base_dir, dist_dir)
    logging.debug(f'removing {dist_dir_path} and all its content')
    shutil.rmtree(dist_dir_path)


def mkdir_safe(dirname):
    """Make the given directory if it doesn't exist.

    Ignore otherwise.
    """
    if not pt.isdir(dirname):
        os.mkdir(dirname)


def is_ignored(filename):
    """Return True if the given file starts with '_'."""
    return pt.basename(filename).startswith('_')
