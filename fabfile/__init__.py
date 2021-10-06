from six.moves import configparser
from fabric.api import env
from fabric.context_managers import cd, prefix
from fabric.decorators import task
from fabric.operations import require, run
from path import path


LOCAL_PATH = path(__file__).abspath().parent
LOCATION_WARNING = """deployment. You need to prefix the task with the location
    i.e.: fab staging deploy."""


def environment(location):
    config = configparser.SafeConfigParser()
    config_path = LOCAL_PATH / 'env.ini'
    config.read(config_path)
    try:
        env.update(config.items(section=location))
    except configparser.NoSectionError:
        exit('Cannot run task on {0}. Please define the corresponding section '
             'in {1}.'.format(location, config_path))
    env.sandbox_activate = 'source {0}'.format(path(env.sandbox) / 'bin' /
                                               'activate')
    env.deployment_location = location


def require_variables():
    require('deployment_location', used_for=LOCATION_WARNING)
    require('project_root', provided_by=[environment])
    require('fixture', provided_by=[environment])


@task
def staging():
    environment('staging')


@task
def production():
    environment('production')


@task
def public():
    environment('public')


@task
def production():
    environment('production')


@task
def deploy():
    require_variables()

    with cd(env.project_root), prefix(env.sandbox_activate):
        run('git pull --rebase')
        run('pip install -r requirements-dep.txt')
        run('./manage.py migrate')
        run('./manage.py collectstatic --noinput')
        run('supervisorctl -c {0} restart django'.format(env.supervisord_conf))


@task
def loaddata():
    require_variables()

    with cd(env.project_root), prefix(env.sandbox_activate):
        run('./manage.py loaddata {0}'.format(
            path(env.project_root) / env.fixture))
