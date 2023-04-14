#
# RTEMS Tools Project (http://www.rtems.org/)
# Copyright 2010-2018,2023 Chris Johns (chrisj@rtems.org)
# All rights reserved.
#
# This file is part of the RTEMS Tools package in 'rtems-tools'.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

#
# Releasing RTEMS Tools
# ---------------------
#
# Format:
#
#  The format is INI. The file requires a `[version`] section and a `revision`
#  option:
#
#   [version]
#   revision = <version-string>
#
#  The `<version-string>` has the `version` and `revision` delimited by a
#  single `.`. An example file is:
#
#   [version]
#   revision = 5.0.not_released
#
#  where the `version` is `5` and the revision is `0` and the package is not
#  released. The label `not_released` is reversed to mean the package is not
#  released. A revision string can contain extra characters after the
#  `revision` number for example `5.0-rc1` or is deploying a package
#  `5.0-nasa-cfs`
#
#  Packages can optionally add specialised sections to a version configuration
#  files. These can be accessed via the:
#
#   load_release_settings: Return the items in a section
#   load_release_setting: Return an item from a section
#
# User deployment:
#
#  Create a git archive and then add a suitable VERSION file to the top
#  directory of the package. The package assumes your python executable is
#  location in `bin` directory which is one below the top of the package's
#  install prefix.
#
# RTEMS Release:
#
#  Set the values in the `rtems-version.ini` file. This is a shared file so
#  packages and encouraged to add specific settings to other configuration
#  files.
#
# Notes:
#
#  This module uses os.apth for paths and assumes all paths are in the host
#  format.
#

from __future__ import print_function

import itertools
import os
import sys

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from . import git
from . import rtems

#
# Default to an internal string.
#
_version = 'undefined'
_revision = 'not_released'
_version_str = '%s.%s' % (_version, _revision)
_released = False
_git = False
_is_loaded = False


def _top(ctx):
    top = ctx.path
    if top == None:
        cts.fatal('no top path found')
    return str(top)


def _load_released_version_config(ctx):
    '''Local worker to load a configuration file.'''
    top = _top(ctx)
    for ver in [os.path.join(top, 'VERSION')]:
        if os.path.exists(os.path.join(ver)):
            v = configparser.SafeConfigParser()
            try:
                v.read(os.path.host(ver))
            except Exception as e:
                raise ctx.fatal('invalid version config format: %s: %s' %
                                (ver, e))
            return ver, v
    return None, None


def _load_released_version(ctx):
    '''Load the release data if present. If not found the package is not
    released.

    A release can be made by adding a file called `VERSION` to the top level
    directory of a package. This is useful for user deploying a package and
    making custom releases.
    '''
    global _version
    global _revision
    global _released
    global _version_str
    global _is_loaded

    if not _is_loaded:
        vc, v = _load_released_version_config(ctx)
        if v is not None:
            try:
                ver_str = v.get('version', 'revision')
            except Exception as e:
                raise ctx.fatal('invalid version file: %s: %s' % (vc, e))
            ver_split = ver_str.split('.')
            if len(ver_split) < 2:
                raise ctx.fatal('invalid version release value: %s: %s' %
                                (vc, ver_str))
            ver = ver_split[0]
            rev = '.'.join(ver_split[1:])
            try:
                _version = int(ver)
            except:
                raise ctx.fatal('invalid version config value: %s: %s' %
                                (vc, ver))
            try:
                _revision = int(''.join(
                    itertools.takewhile(str.isdigit, str(rev))))
            except Exception as e:
                raise ctx.fatal('Invalid revision config value: %s: %s: %s' %
                                (vc, rev, e))
            if not 'not_released' in ver:
                _released = True
            _version_str = ver_str
            _is_loaded = True
    return _released


def _load_git_version(ctx):
    global _version
    global _revision
    global _git
    global _version_str
    repo = git.repo(ctx, _top(ctx))
    if repo.valid():
        head = repo.head()
        if repo.dirty():
            modified = 'modified'
            revision_sep = '-'
            sep = ' '
        else:
            modified = ''
            revision_sep = ''
            sep = ''
        _revision = '%s%s%s' % (head[0:12], revision_sep, modified)
        _version_str += ' (%s%s%s)' % (head[0:12], sep, modified)
        _git = True
    return _git


def load_release_settings(ctx, section, error=False):
    vc, v = _load_released_version_config(ctx)
    items = []
    if v is not None:
        try:
            items = v.items(section)
        except Exception as e:
            if not isinstance(error, bool):
                error(e)
            elif error:
                raise ctx.fatal('Invalid config section: %s: %s: %s' %
                                (vc, section, e))
    return items


def load_release_setting(ctx, section, option, raw=False, error=False):
    vc, v = _load_released_version_config()
    value = None
    if v is not None:
        try:
            value = v.get(section, option, raw=raw)
        except Exception as e:
            if not isinstance(error, bool):
                error(e)
            elif error:
                raise ctx.fatal('Invalid config section: %s: %s: %s.%s' %
                                (vc, section, option, e))
    return value


def load_rtems_version_header(ctx, rtems_version, arch_bsp, incpaths):
    global _version
    global _revision
    global _version_str
    for inc in incpaths:
        header = os.path.join(inc, 'rtems/score/cpuopts.h')
        if os.path.exists(header):
            try:
                with open(header, 'r') as h:
                    text = h.readlines()
            except:
                ctx.fatal('cannot read: ' + header)
            for l in text:
                ls = l.split()
                if len(ls) == 3:
                    if ls[1] == '__RTEMS_MAJOR__':
                        _version = int(ls[2])
                    elif ls[1] == '__RTEMS_REVISION__':
                        _revision = int(ls[2])
                    elif ls[1] == 'RTEMS_VERSION':
                        _version_str = ls[2][1:-1]
            _is_loaded = True
            break


def released(ctx):
    return _load_released_version(ctx)


def version_control(ctx):
    return _load_git_version(ctx)


def string(ctx):
    _load_released_version(ctx)
    _load_git_version(ctx)
    return _version_str


def version(ctx):
    _load_released_version(ctx)
    _load_git_version(ctx)
    return _version


def revision(ctx):
    _load_released_version(ctx)
    _load_git_version(ctx)
    return _revision
