#
# RTEMS Project (https://www.rtems.org/)
#
# Copyright (c) 2017 Chris Johns <chrisj@rtems.org>. All rights reserved.
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

def tar(ctx, name, target, root):
    top = ctx.path.get_src().find_node(root)
    source = ctx.path.get_src().ant_glob(root + '/**')
    ctx(rule = 'tar -C %s -cf ${TGT} .' % (top),
        name = name,
        target = target,
        source = source,
        root = root,
        color = 'CYAN')

def bin2c(ctx, name, target, source):
    ctx(rule = '${RTEMS_BIN2C} ${SRC} ${TGT}',
        name = name,
        target = target,
        source = source,
        color = 'PINK')

def build(bld, name, root):
    """ The source is the C file that includes the header file."""
    tar(bld,
        name = name + '-tar',
        target = name + '.tar',
        root = root)
    bin2c(bld,
          name = name,
          target = name + '-tar.c',
          source = name + '.tar')
    bld.add_group()
