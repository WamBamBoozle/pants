# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (absolute_import, division, generators, nested_scopes, print_function,
                        unicode_literals, with_statement)

import errno
import os
import shutil

from pants.backend.jvm.subsystems.jvm_tool_mixin import JvmToolMixin
from pants.backend.jvm.tasks.bootstrap_jvm_tools import BootstrapJvmTools
from pants.base.config import Config
from pants.base.extension_loader import load_plugins_and_backends
from pants.ivy.bootstrapper import Bootstrapper
from pants.option.options_bootstrapper import OptionsBootstrapper
from pants.util.dirutil import safe_mkdir, safe_mkdtemp, safe_walk
from pants_test.tasks.task_test_base import TaskTestBase


class JvmToolTaskTestBase(TaskTestBase):
  """Prepares an ephemeral test build root that supports tasks that use jvm tool bootstrapping."""

  @property
  def alias_groups(self):
    return load_plugins_and_backends().registered_aliases()

  def setUp(self):
    # TODO(Eric Ayers): this is the old way
    # Ensure we get a read of the real pants.ini config
    Config.reset_default_bootstrap_option_values()
    real_config = Config.from_cache()

    super(JvmToolTaskTestBase, self).setUp()

    # Use a synthetic subclass for bootstrapping within the test, to isolate this from
    # any bootstrapping the pants run executing the test might need.
    self.bootstrap_task_type, bootstrap_scope = self.synthesize_task_subtype(BootstrapJvmTools)
    JvmToolMixin.reset_registered_tools()

    # Cap BootstrapJvmTools memory usage in tests.  The Xmx was empirically arrived upon using
    # -Xloggc and verifying no full gcs for a test using the full gamut of resolving a multi-jar
    # tool, constructing a fat jar and then shading that fat jar.
    self.set_options_for_scope(bootstrap_scope, jvm_options=['-Xmx128m'])

    def link_or_copy(src, dest):
      try:
        os.link(src, dest)
      except OSError as e:
        if e.errno == errno.EXDEV:
          shutil.copy(src, dest)
        else:
          raise e

    def link(path, optional=False, force=False):
      src = os.path.join(self.real_build_root, path)
      if not optional or os.path.exists(src):
        dest = os.path.join(self.build_root, path)
        safe_mkdir(os.path.dirname(dest))
        try:
          link_or_copy(src, dest)
        except OSError as e:
          if force and e.errno == errno.EEXIST:
            os.unlink(dest)
            link_or_copy(src, dest)
          else:
            raise e
        return dest

    def link_tree(path, optional=False, force=False):
      src = os.path.join(self.real_build_root, path)
      if not optional or os.path.exists(src):
        for abspath, dirs, files in safe_walk(src):
          for f in files:
            link(os.path.relpath(os.path.join(abspath, f), self.real_build_root), force=force)

    # TODO(John Sirois): Find a way to do this cleanly
    link('pants.ini', force=True)

    # TODO(pl): Note that this pulls in a big chunk of the hairball to every test that
    # depends on it, because BUILD contains source_roots that specify a variety of types
    # from different backends.
    link('BUILD', force=True)

    link('BUILD.tools', force=True)
    support_dir = real_config.getdefault('pants_supportdir')
    link_tree(os.path.relpath(os.path.join(support_dir, 'ivy'), self.real_build_root), force=True)
    bootstrap_option_values = OptionsBootstrapper().get_bootstrap_options().for_global_scope()
    self.set_bootstrap_options(bootstrap_option_values)
    safe_mkdir(os.path.join(bootstrap_option_values.pants_supportdir, 'ivy'))
    settings_file = os.path.join(bootstrap_option_values.pants_supportdir, 'ivy', 'ivysettings.xml')
    if not os.path.exists(settings_file):
      shutil.copy('build-support/ivy/ivysettings.xml',
                  os.path.join(bootstrap_option_values.pants_supportdir, 'ivy'))
    Bootstrapper.reset_instance()

  def context(self, for_task_types=None, options=None, target_roots=None,
              console_outstream=None, workspace=None, register_bootstrap_opts=True):
    # Add in the bootstrapper task type, so its options get registered and set.
    for_task_types = [self.bootstrap_task_type] + (for_task_types or [])
    return super(JvmToolTaskTestBase, self).context(for_task_types=for_task_types,
                                                    options=options,
                                                    target_roots=target_roots,
                                                    console_outstream=console_outstream,
                                                    workspace=workspace,
                                                    register_bootstrap_opts=register_bootstrap_opts)

  def prepare_execute(self, context, workdir):
    """Prepares a jvm tool using task for execution, ensuring any required jvm tools are
    bootstrapped.

    NB: Other task pre-requisites will not be ensured and tests must instead setup their own product
    requirements if any.

    :returns: The prepared Task
    """
    # TODO(John Sirois): This is emulating Engine behavior - construct reverse order, then execute;
    # instead it should probably just be using an Engine.
    task = self.create_task(context, workdir)
    task.invalidate()
    bootstrap_workdir = os.path.join(workdir, '_bootstrap_jvm_tools')
    self.bootstrap_task_type(context, bootstrap_workdir).execute()
    return task

  def execute(self, context):
    """Executes the given task ensuring any required jvm tools are bootstrapped.

    NB: Other task pre-requisites will not be ensured and tests must instead setup their own product
    requirements if any.

    :returns: The Task that was executed
    """
    # TODO(John Sirois): This is emulating Engine behavior - construct reverse order, then execute;
    # instead it should probably just be using an Engine.
    workdir = safe_mkdtemp(dir=self.build_root)
    task = self.prepare_execute(context, workdir)
    task.execute()
    return task
