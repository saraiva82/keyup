"""

keyup :  Copyright 2017-2019, Blake Huber

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

see: https://www.gnu.org/licenses/#GPL

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
contained in the program LICENSE file.

"""

import os
import sys
import platform
import subprocess
from shutil import which
from shutil import copy2 as copyfile
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from pathlib import Path
from codecs import open
import keyup


requires = [
    'awscli>=1.16.100',
    'boto3>=1.10.1',
    'distro>=1.4.0',
    'libtools>=0.4.2',
    'pyaws>=0.4.1',
    'pytz>=2019.1',
    'prompt-toolkit>=3.0.10',
    'veryprettytable>=0.8.1'
]


_project = 'keyup'
_root = os.path.abspath(os.path.dirname(__file__))
_comp_fname = 'keyup-completion.bash'
_iamusers_fname = 'iam_users.py'


def _root_user():
    """
    Checks localhost root or sudo access
    """
    if os.geteuid() == 0:
        return True
    elif subprocess.getoutput('echo $EUID') == '0':
        return True
    return False


def create_artifact(object_path, type):
    """Creates post install filesystem artifacts"""
    if type == 'file':
        with open(object_path, 'w') as f1:
            f1.write(sourcefile_content())
    elif type == 'dir':
        os.makedirs(object_path)


def os_parityPath(path):
    """
    Converts unix paths to correct windows equivalents.
    Unix native paths remain unchanged (no effect)
    """
    path = os.path.normpath(os.path.expanduser(path))
    if path.startswith('\\'):
        return 'C:' + path
    return path


class PostInstallDevelop(develop):
    """ post-install, development """
    def run(self):
        subprocess.check_call("bash scripts/post-install-dev.sh".split())
        develop.run(self)


class PostInstall(install):
    """
    Summary.

        Postinstall script to place bash completion artifacts
        on local filesystem

    """
    def valid_os_shell(self):
        """
        Summary.

            Validates install environment for Linux and Bash shell

        Returns:
            Success | Failure, TYPE bool

        """
        if platform.system() == 'Windows':
            return False
        elif which('bash'):
            return True
        elif 'bash' in subprocess.getoutput('echo $SHELL'):
            return True
        return False

    def run(self):
        """
        Summary.

            Executes post installation configuration only if correct
            environment detected

        """
        completion_file = os.path.join(user_home(), '.bash_completion')
        completion_dir = os.path.join(user_home(), '.bash_completion.d')
        config_dir = os.path.join(user_home(), '.config', _project)

        if self.valid_os_shell() and not _root_user():

            # target home directories
            if not os.path.exists(os_parityPath(completion_file)):
                create_artifact(os_parityPath(completion_file), 'file')
            if not os.path.exists(os_parityPath(completion_dir)):
                create_artifact(os_parityPath(completion_dir), 'dir')
            if not os.path.exists(os_parityPath(config_dir)):
                create_artifact(os_parityPath(config_dir), 'dir')

            ## ensure installation of home directory artifacts (data_files) ##

            # bash_completion;
            if not os.path.exists(os_parityPath(os.path.join(completion_dir, _comp_fname))):
                copyfile(
                    os_parityPath(os.path.join('bash', _comp_fname)),
                    os_parityPath(os.path.join(completion_dir, _comp_fname))
                )

            if not os.path.exists(os.path.join(config_dir, _iamusers_fname)):
                copyfile(
                    os_parityPath(os.path.join('bash', _iamusers_fname)),
                    os_parityPath(os.path.join(config_dir, _iamusers_fname))
                )
        install.run(self)


def preclean(dst):
    if os.path.exists(dst):
        os.remove(dst)
    return True


def read(fname):
    basedir = os.path.dirname(sys.argv[0])
    return open(os.path.join(basedir, fname)).read()


def sourcefile_content():
    sourcefile = """
    for bcfile in ~/.bash_completion.d/* ; do
        [ -f "$bcfile" ] && . $bcfile
    done\n
    """
    return sourcefile


def user_home():
    """Returns os specific home dir for current user"""
    try:
        if platform.system() == 'Linux' or platform.system() == 'Darwin':
            if _root_user() and os.environ.get('SUDO_USER'):
                return '/home/{}'.format(os.getenv('SUDO_USER'))
            return str(Path.home())

        elif platform.system() == 'Windows':
            username = os.getenv('username')
            return 'C:\\Users\\' + username

        elif platform.system() == 'Java':
            print(f'Unsupported of {os_type}')
            sys.exit(1)
    except OSError as e:
        raise e


# branch install based on user priviledge level

if _root_user():

    setup(
        name=_project,
        version=keyup.__version__,
        description='Automated IAM Access Key Rotation for Amazon Web Services',
        long_description=read('DESCRIPTION.rst'),
        url='http://keyup.readthedocs.io',
        author=keyup.__author__,
        author_email=keyup.__email__,
        license='GPL-3.0',
        classifiers=[
            'Topic :: Security',
            'Development Status :: 5 - Production/Stable',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: POSIX :: Linux',
            'Operating System :: Microsoft :: Windows'
        ],
        keywords='Amazon Web Services iam credentials AWS access key secret key',
        packages=find_packages(exclude=['assets', 'docs', 'reports', 'scripts', 'tests']),
        include_package_data=True,
        install_requires=requires,
        python_requires='>=3.6, <4',
        data_files=[
            (
                os.path.join('/etc/bash_completion.d'),
                [os.path.join('bash', _comp_fname)]
            ),
            (
                os.path.join(user_home(), '.config', _project),
                [os.path.join('bash', _iamusers_fname)]
            )
        ],
        entry_points={
            'console_scripts': [
                'keyup=keyup.cli:init',
                'keyconfig=keyup.keyconfig:option_configure'
            ]
        },
        zip_safe=False
    )

else:

    # non-priviledged user

    setup(
        name=_project,
        version=keyup.__version__,
        description='Automated IAM Access Key Rotation for Amazon Web Services',
        long_description=read('DESCRIPTION.rst'),
        url='http://keyup.readthedocs.io',
        author=keyup.__author__,
        author_email=keyup.__email__,
        license='GPL-3.0',
        classifiers=[
            'Topic :: Security',
            'Development Status :: 5 - Production/Stable',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: POSIX :: Linux',
            'Operating System :: Microsoft :: Windows'
        ],
        keywords='Amazon Web Services iam credentials AWS access key secret key',
        packages=find_packages(exclude=['assets', 'docs', 'reports', 'scripts', 'tests']),
        include_package_data=True,
        install_requires=requires,
        python_requires='>=3.6, <4',
        cmdclass={
            'install': PostInstall
        },
        data_files=[
            (
                os.path.join(user_home(), '.bash_completion.d'),
                [os.path.join('bash', _comp_fname)]
            ),
            (
                os.path.join(user_home(), '.config', _project),
                [os.path.join('bash', _iamusers_fname)]
            )
        ],
        entry_points={
            'console_scripts': [
                'keyup=keyup.cli:init',
                'keyconfig=keyup.keyconfig:option_configure'
            ]
        },
        zip_safe=False
    )
