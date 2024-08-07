RTEMS Waf
=========

RTEMS Waf is a module that supports the Waf build system and RTEMS. The module
is integrated into a project or library providing Waf build support to create
RTEMS libraries or executable.

RTEMS Waf provides:

  * Checking for a valid RTEMS installation of tools and kernel.
  * Support for multiple versions of RTEMS.
  * Support to build a number of BSPs at once.
  * Support for the RTEMS tools and kernel being installed under a shared or
    separate prefixes [2].
  * Flexible integration that allows easy project specific specialization.
  * Support to check which features RTEMS is built with.
  * Support for BSP compiler and linker flags. The flags are separated into 
    their various types to allow flexible options management in a project.
  * Support to list the available architectures and BSPs.
  * Additional support for creating root file systems for RTEMS targets.


Bugs
----

Please report issues to the rtems_waf GitLab:

  https://gitlab.rtems.org/rtems/tools/rtems_waf

Feedback is always welcome.

Waf
---

You can find the Waf project here:

  https://waf.io/

Waf does not come as a package in distributions so you need to download and
install it.

  1. Waf is a Python program so you will also need to have a current Python
     installed and accessible via your environment's path.

  2. Download the latest signed Waf executable file from the Waf website.

  3. Place the waf executable in a personal directory that is in your path, for
     example $HOME/bin. Modify the file's permissions so it can be executed:

     ```shell
     $ chmod +x $HOME/bin/waf
     ```

Git Submodule
-------------

RTEMS Waf can be used as a git submodule. This lets a number of projects share
the common waf support.

  1. Add RTEMS Waf a git submodule to your project:

     ```shell
     $ cd my_project
     $ git submodule add https://gitlab.rtems.org/rtems/tools/rtems_waf.git rtems_waf
     ```

  2. Initialize the submodule(s) for your project:

     ```shell
     $ git submodule init
     ```

  3. Update the RTEMS Waf submodule:
 
     ```shell
     $ git submodule update rtems_waf
     ```

     Note: the `rtems_waf` submodule name is provided as some projects 
           may have other submodules you may not wish to update.

  4. When submodules are added they are headless which means they are not on a
     current branch. Switch to a branch:

     ```shell
     $ cd rtems_waf
     $ git checkout master
     $ cd ..
     ```

     Note: you can replace `master` in the `checkout` above with any valid 
           branch in the RTEMS Waf repo.

  5. Update the RTEMS Waf submodule to the latest version on the selected 
     branch:

     ```shell
     $ cd rtems_waf
     $ git pull
     $ cd ..
     ```

  6. Check the new submodule is part of your project and ready to be committed:

     ```shell
     $ git status
     ```

     The `rtems_waf` module will be listed as `modified`.

  7. Commit the change by adding it to your staged files:

     ```shell
     $ git add rtems_waf
     ```

     When ready commit:

     ```shell
     $ git commit
     ```

     Review the changes and if they are correct push them:

     ```shell
     $ git log -p
     $ git push
     ```

The RTEMS Waf module is updated from time to time as new features are added or
changes happen in waf. To update a project's existing RTEMS Waf submodule
perform steps 5. to 7.


Project Instructions
--------------------

Create a `README.waf` file in your project and add the Waf installation section,
your project specific options and the following steps. These steps are for
RTEMS 5, change for the specific version of RTEMS your project supports.

  1. Build or install the tools. In this example the path is the personal prefix
     of $HOME/development/rtems/5 [^1].

  2. Build and install the RTEMS Board Support Packages you want to use. In this
     example separate tools and kernel prefixes are used [^2]. The kernel path is
     $HOME/development/rtems/bsps/5.

  3. Unpack this package somewhere, anywhere on your disk and change into the top
     level directory.

  4. Populate the git submodule:

     ```shell
     $ git submodule init
     $ git submodule update rtems_waf
     ```

  5. Configure with your specific settings. In this case the path to the tools
     and the kernel are separate and provided on the command line. Your
     environment's path variable does not need to changed [^3]. We limit the build
     to `sparc/erc32` BSP:

     ```shell
     $ waf configure --rtems=$HOME/development/rtems/bsps/5 \
                     --rtems-tools=$HOME/development/rtems/5 \
                     --rtems-bsps=sparc/erc32

     You can use `--rtems-archs=sparc,i386` or
     `--rtems-bsps=sparc/erc32,i386/pc586` to build more than BSP at a time.

  6. Build:

     `$ waf`


An RTEMS Waf Project
--------------------

RTEMS Waf provides a base to build RTEMS application.

Waf provides a build system framework. You can use waf in your project by
simply providing a list of files you wish to build and link to create an
executable or you can use waf as framework which is integrated into your
project to become is build system.


Importing RTEMS Waf
-------------------

Using RTEMS Waf as a submodule means it may not be present if the submodules
have not been initialized and updated. This results in a Python error. The
following import is recommended so a user friendly error is reported:

```python
 from __future__ import print_function

 try:
     import rtems_waf.rtems as rtems
 except:
     print('error: no rtems_waf git submodule; see README.waf', file = stderr)
     import sys
     sys.exit(1)
```

Initialization
--------------

The `wscript` `init()` function is called early in waf's processing. The RTEMS
Waf's `init()` call lets you provide:

  1. Filters

  2. RTEMS Version

  3. Long command line control

  4. Waf BSP initialization hook

A example call to RTEMS Waf's `init()` is:

  ```python
  rtems_version = "5"

  def init(ctx):
      rtems.init(ctx, version = rtems_version, long_commands = True)
  ```

Filters provide a way to control the tools, architectures and BSPs your project
supports. RTEMS Waf scans and finds all installed RTEMS tool sets and BSPs and
your project may only support a limited number of these. Filtering provides a
way for your project to control what RTEMS Waf accepts and rejects when
automatically scanning the installed tools and RTEMS kernels. A filter is a
Python dictionary and the following example will accept `arm` and `sparc` tool
chains and filtering out the `bfin` tool chain. The filter will only build the
`arm` architecture and will accept all BSPs except ones starting with `lpc` if
they are installed:

  ```python
  my_filter = { 'tools': { 'in': ['arm', 'sparc'], 'out': ['bfin'] },
                'arch':  { 'in': ['arm'],          'out': [] },
		'bsps':  { 'in': [],               'out': ['lpc.*'] } }
  ```

There are three (3) filters the `tools`, `archs` and `bsps` and each of these
filter types has an `in` and `out` list. The `in` and `out` items are Python
regular expressions.

The RTEMS Version lets your project provide the default RTEMS version. This can
be overridden by the configure option `--rtems-version`.

Long commands is specific to Windows and provides support for tool command
lines that are longer than the standard Windows command shell's limit. The
support is based on the example available in Waf extra's.

The Waf BSP initialization hook is a function called as part of the RTEMS Waf's
`init()` call with the Waf environment and list of BSP contexts. This hook can
be used to provide specialized BSP support.

Options
-------

The `wscript` `option()` function is called to collect command line options for
Waf argument processing.

A example call to RTEMS Waf's `options()` is:

  ```python
  def options(opt):
      rtems.options(opt)
  ```

Configure
---------

The `wscript` `configure()` function is called when Waf is configuring a
build. The RTEMS Waf's `configure()` lets you provide:

  1. Waf BSP configure hook

A example call to RTEMS Waf's `configure()` is:

  ```python
  def configure(conf):
      rtems.configure(conf)
  ```

The BSP configure hook is called at end of a BSP's configuration. The BSP's
`conf` variable and the `arch/bsp` are passed as arguments. The `arch/bsp` is
the RTEMS standard for specifying a BSP, for example `sparc/erc32`. The BSP
configure support can be used to check a BSP for header, check an RTEMS feature
is present for a specific BSP or add per BSP build variant support:

  ```python
  def bsp_configure(conf, arch_bsp):
      conf.check(header_name = "dlfcn.h", features = "c")
      conf.check(header_name = "rtems/pci.h", features = "c", mandatory = False)
      if not rtems.check_posix(conf):
          conf.fatal("POSIX is disabled; configure RTEMS with --enable-posix")
      env = conf.env.derive()
      for builder in builders:
          ab = conf.env.RTEMS_ARCH_BSP
          variant = ab + "-" + builder
          conf.msg('Configure variant: ', variant)
          conf.setenv(variant, env)
          build_variant_bsp_configure(conf, arch_bsp)
          conf.setenv(ab)
  ```


Build
-----

The `wscript` `build()` function is called when Waf is asking what to
build.

A example call to RTEMS Waf's `build()` is:

  ```python
  def build(bld):
      rtems.build(bld)
      bld(features = 'c cprogram',
          target = 'hello.exe',
          source = ['hello.c'])
  ```

In this example the C source file `hello.c` is compiled and linked to create
the RTEMS executable `hello.exe`. The build is within the context of the BSP.


Example
-------

Save the following as `wscript`:

  ```python
  #
  # Example Waf build script for RTEMS
  #
  # To configure, build and run:
  #
  # $ waf configure --rtems=$HOME/development/rtems/build/5 \
  #                 --rtems-tools=$HOME/development/rtems/5 \
  #                 --rtems-bsps=sparc/erc32
  # $ waf
  # $ $HOME/development/rtems/5/bin/sparc-rtems5-run \
  #                             ./build/sparc-rtems5-erc32/hello.exe
  #
  # You can use '--rtems-archs=sparc,i386' or
  # '--rtems-bsps=sparc/erc32,i386/pc586' to build for more than one BSP at a
  # time.
  #

  from __future__ import print_function

  rtems_version = "5"

  try:
      import rtems_waf.rtems as rtems
  except:
      print('error: no rtems_waf git submodule; see README.waf', file = stderr)
      import sys
      sys.exit(1)

  def init(ctx):
      rtems.init(ctx, version = rtems_version, long_commands = True)

  def options(opt):
      rtems.options(opt)

  def configure(conf):
      rtems.configure(conf)

  def build(bld):
      rtems.build(bld)
      bld.env.CFLAGS += ['-O2','-g']
      bld(features = 'c cprogram',
          target = 'hello.exe',
          source = ['hello.c'])
  ```

Save the example C hello world as `hello.c`:

  ```python
  #include <rtems.h>
  #include <stdlib.h>
  #include <stdio.h>

  rtems_task Init(rtems_task_argument ignored) {
    printf("Hello World\n");
    exit(0);
  }

  /* configuration information */
  #include <bsp.h>
  #define CONFIGURE_APPLICATION_DOES_NOT_NEED_CLOCK_DRIVER
  #define CONFIGURE_APPLICATION_NEEDS_CONSOLE_DRIVER
  #define CONFIGURE_USE_DEVFS_AS_BASE_FILESYSTEM
  #define CONFIGURE_RTEMS_INIT_TASKS_TABLE
  #define CONFIGURE_MAXIMUM_TASKS 1
  #define CONFIGURE_INIT
  #include <rtems/confdefs.h>
  ```

[^1]: A personal prefix is private to you and located where you have enough disk
      space to complete an RTEMS installation. We often show this as your home
      directory ($HOME) because it works on machines you may not have root access
      to and cannot configure. We recommend you never work as root on a machine
      you control.

[^2]: RTEMS supports shared or separate tool and kernel prefixes. The prefix is
      the path given to the tools and kernel when building and is the path the
      tools or kernel are installed into when you run the install phase of a
      build. A shared tools and kernel prefix is often used with releases 
      because the tools and kernel in a release are matched and do not change. 
      Separate tools and kernel paths can be used if you have a common tool set 
      with changing kernel versions. This tends to happen when you are testing 
      kernel patches or changes.

[^3]: It is good practice to keep your environment as empty as possible. Using
      the environment to set paths to tools or specific values to configure and
      control builds is dangerous because settings can leak between different
      builds and change what you expect or not been and seen and lost. The waf
      tool used here lets you specify on the command line the tools and RTEMS
      paths and this is embedded in waf's configuration information. If you have
      a few source trees working at any one time with different tool sets or
      configurations you can easily move between them safe in the knowledge that
      one build will not affect another.
