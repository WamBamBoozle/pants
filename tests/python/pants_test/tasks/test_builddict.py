# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from contextlib import closing
from StringIO import StringIO

from pants.backend.core.tasks.builddictionary import BuildBuildDictionary, assemble
from pants.base.build_configuration import BuildConfiguration
from pants.base.build_file_parser import BuildFileParser
from pants.util.dirutil import safe_rmtree
from pants_test.tasks.test_base import TaskTest, prepare_task


OUTDIR = "/tmp/dist1"

sample_ini_test_1 = """
[DEFAULT]
outdir: %s
""" % OUTDIR


class BaseBuildBuildDictionaryTest(TaskTest):

  def setUp(self):
    safe_rmtree(OUTDIR)

  def execute_task(self, config=sample_ini_test_1):
    with closing(StringIO()) as output:
      task = prepare_task(BuildBuildDictionary, config=config)
      task.execute()
      return output.getvalue()

  def tearDown(self):
    safe_rmtree(OUTDIR)


class BuildBuildDictionaryTestEmpty(BaseBuildBuildDictionaryTest):
  def test_builddict_empty(self):
    """Execution should be silent."""
    # We don't care _that_ much that execution be silent. Nice if at least
    # one test executes the task and doesn't explode, tho.
    self.assertEqual('', self.execute_task())


class ExtractedContentSanityTests(BaseBuildBuildDictionaryTest):
  def test_invoke_assemble(self):
    bfp = BuildFileParser(BuildConfiguration(), '.')
    # we get our doc'able symbols from a BuildFileParser.
    # Invoke that functionality without blowing up:
    syms = assemble(build_file_parser=bfp)
    # These symbols snuck into old dictionaries, make sure they don't again:
    for unexpected in ['__builtins__', 'Target']:
      self.assertTrue(unexpected not in syms.keys(), "Found %s" % unexpected)
