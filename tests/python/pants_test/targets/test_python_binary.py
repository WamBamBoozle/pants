# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import pytest

from pants.base.address import SyntheticAddress
from pants.base.exceptions import TargetDefinitionException
from pants.python.targets.python_binary import PythonBinary
from pants_test.base_test import BaseTest


class TestPythonBinary(BaseTest):
  def test_python_binary_must_have_some_entry_point(self):
    with pytest.raises(TargetDefinitionException):
      self.make_target(spec=':binary', target_type=PythonBinary)

  def test_python_binary_with_entry_point_no_source(self):
    assert self.make_target(spec=':binary',
                            target_type=PythonBinary,
                            entry_point = 'blork').entry_point == 'blork'

  def test_python_binary_with_source_no_entry_point(self):
    assert self.make_target(spec=':binary1',
                            target_type=PythonBinary,
                            source = 'blork.py').entry_point == 'blork'
    assert self.make_target(spec=':binary2',
                            target_type=PythonBinary,
                            source = 'bin/blork.py').entry_point == 'bin.blork'

  def test_python_binary_with_entry_point_and_source(self):
    assert 'blork' == self.make_target(spec=':binary1',
                                       target_type=PythonBinary,
                                       entry_point = 'blork',
                                       source='blork.py').entry_point
    assert 'blork:main' == self.make_target(spec=':binary2',
                                            target_type=PythonBinary,
                                            entry_point = 'blork:main',
                                            source='blork.py').entry_point
    assert 'bin.blork:main' == self.make_target(spec=':binary3',
                                                target_type=PythonBinary,
                                                entry_point = 'bin.blork:main',
                                                source='bin/blork.py').entry_point

  def test_python_binary_with_entry_point_and_source_mismatch(self):
    with pytest.raises(TargetDefinitionException):
      self.make_target(spec=':binary1',
                       target_type=PythonBinary,
                       entry_point = 'blork',
                       source='hork.py')
    with pytest.raises(TargetDefinitionException):
      self.make_target(spec=':binary2',
                       target_type=PythonBinary,
                       entry_point = 'blork:main',
                       source='hork.py')
    with pytest.raises(TargetDefinitionException):
      self.make_target(spec=':binary3',
                       target_type=PythonBinary,
                       entry_point = 'bin.blork',
                       source='blork.py')
    with pytest.raises(TargetDefinitionException):
      self.make_target(spec=':binary4',
                       target_type=PythonBinary,
                       entry_point = 'bin.blork',
                       source='bin.py')
