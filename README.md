# Webloft
Webloft is a static page generator. Mostly for HTML websites. The user creates a set of configuration files (YAML files) and completes the files with a set of information (name, description, contacts, etc.). When webloft is called, it will generate a set of pages (based on a given template) by inserting the user's data.

## Why
Especially in very static contexts, like an informative personal website, I strictly believe that good old static pages are the right path.

While there are other solutions out there for static sites, I find many of them either too limited or too engineered.
This is how the idea came into being, a static page generator with enough potential to reach the moon, but without all the bloat.

## Basic usage
The tool can be installed via the typical `setup.py` or can be used directly through `main.py`.

When installed, the tool can be called simply by the use of the `webloft` command.

```
webloft [path]
```

The given `path` (default: current directory) should lead to a directory having the following structure:

* index.yaml
* logo.png
* project_directory1
    * project.yaml
* project_directory2
    * project.yaml
* project_directory...

YAML files are where the user data goes. Webloft will read the data and use it to
customize one of its internal templates. The result will be found in the `dist`
directory (a bunch of html and css files, completed with the user data).

`index.yaml` is the **only** mandatory file. Project subdirectories will be used
to generate the "projects" page.

Example `index.yaml`:

```
name: Sherlock Holmes
description: 'Definitely the **best** detective you can dream of.'
contacts:
  - name: Address
    display: 221B Baker Street
```
For more info on how the project is structured and how to use it, please refer to the [wiki](https://github.com/Ball-Man/webloft/wiki).

## FAQ

> Can I build my own template?

With enough understanding of the project's structure, yes.

> Is Internet Explorer supported?

If you're using this tool to build your resumee, you probably don't want to work
for anyone reading it with IE. The main template does not support IE.
