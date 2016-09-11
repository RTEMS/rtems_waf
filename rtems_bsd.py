#
# RTEMS Project (https://www.rtems.org/)
#
# Copyright (c) 2016 Chris Johns <chrisj@rtems.org>. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function

import os.path

try:
    import rtems_waf.rtems as rtems
except:
    print("error: no rtems_waf module")
    import sys
    sys.exit(1)

def init(ctx):
    pass

def options(opt):
    opt.add_option('--net-test-config',
                   default = 'config.inc',
                   dest = 'net_config',
                   help = 'Network test configuration.')
    opt.add_option('--rtems-libbsd',
                   action = 'store',
                   default = None,
                   dest = 'rtems_libbsd',
                   help = 'Path to install RTEMS LibBSD (defauls to prefix).')

def bsp_configure(conf, arch_bsp):
    conf.check(header_name = 'dlfcn.h', features = 'c')
    if not rtems.check_posix(conf):
        conf.fatal("RTEMS kernel POSIX support is disabled; configure RTEMS with --enable-posix")
    if rtems.check_networking(conf):
        conf.fatal("RTEMS kernel contains the old network support; configure RTEMS with --disable-networking")
    if conf.options.rtems_libbsd is None:
        rtems_libbsd_path = conf.env.PREFIX
    else:
        if not os.path.exists(conf.options.rtems_libbsd):
            conf.fatal('RTEMS LibBSD not found')
        rtems_libbsd_path = conf.options.rtems_libbsd

    rtems_libbsd_inc_path = os.path.join(rtems_libbsd_path,
                                         rtems.arch_bsp_include_path(conf.env.RTEMS_VERSION,
                                                                     conf.env.RTEMS_ARCH_BSP))
    rtems_libbsd_lib_path = os.path.join(rtems_libbsd_path,
                                         rtems.arch_bsp_lib_path(conf.env.RTEMS_VERSION,
                                                                 conf.env.RTEMS_ARCH_BSP))

    conf.env.IFLAGS += [rtems_libbsd_inc_path]
    conf.check(header_name = 'machine/rtems-bsd-sysinit.h', features = 'c', includes = conf.env.IFLAGS)

    conf.env.INCLUDES = conf.env.IFLAGS
    conf.env.LIBPATH += [rtems_libbsd_lib_path]
    conf.env.LIB += ['bsd', 'z', 'm']
