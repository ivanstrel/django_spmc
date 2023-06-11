# Django_SPMC

A django app for manual classification of satellite images based on superpixel segmentation.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

License: MIT

## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    $ mypy django_spmc

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

## Deployment

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).

#### Docker usage with PyCharm

Follow [instruction](https://github.com/cookiecutter/cookiecutter-django/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/docs/pycharm/configuration.rst)

The only difference is the `python_interpreater_path` on
the _"Switch to Docker Compose and select local.yml file from directory of your project, next set Service name to django"_
step, in docs it is `python`, but we have to specify absolute path, that is `/usr/local/bin/python`

To launch app initiate docker-compose services through terminal `docker-compose -f local.yml up` or with Pycharm
services tab [Alt+8]

_In development mode, the running app could be accessed at `http:\localhost:3000` -- it is aa devserver of webpack.
classical path `0.0.0.0:8080` would not be able to access statics._

To launch python console use **"Tools --> Python or Debug Console"**

#### Accessing docker terminal

1. Launch the docker compose in terminal: `docker-compose -f local.yml up`. Alternatively use Pycharm
   services tab [Alt+8]
2. Add another terminal and connect to `django` service with `docker-compose -f local.yml exec django sh`. In such a
   way you can work with file system if needed. Though, commands like `manage.py migrate` throws errors.
3. You can call `manage.py` by direct invocation of commands through docker-composer exec, for example
   `docker-compose -f local.yml run --rm django python manage.py startapp spmc`

#### Install new packages

1. Edit `reuirements/base[local, production].txt` files, add required packages
2. Run `docker-compose -f local.yml build` from a terminal

### Custom Bootstrap Compilation

The generated CSS is set up with automatic Bootstrap recompilation with variables of your choice.
Bootstrap v5 is installed using npm and customised by tweaking your variables in `static/sass/custom_bootstrap_vars`.

You can find a list of available variables [in the bootstrap source](https://github.com/twbs/bootstrap/blob/v5.1.3/scss/_variables.scss), or get explanations on them in the [Bootstrap docs](https://getbootstrap.com/docs/5.1/customize/sass/).

Bootstrap's javascript as well as its dependencies are concatenated into a single file: `static/js/vendors.js`.
