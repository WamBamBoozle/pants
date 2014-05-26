# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import os

from pants.jvm.targets.annotation_processor import AnnotationProcessor
from pants.jvm.targets.artifact import Artifact
from pants.jvm.targets.benchmark import Benchmark
from pants.jvm.targets.credentials import Credentials
from pants.jvm.targets.jar_dependency import JarDependency
from pants.jvm.targets.jar_library import JarLibrary
from pants.jvm.targets.java_agent import JavaAgent
from pants.jvm.targets.java_antlr_library import JavaAntlrLibrary
from pants.jvm.targets.java_library import JavaLibrary
from pants.jvm.targets.java_protobuf_library import JavaProtobufLibrary
from pants.jvm.targets.java_tests import JavaTests
from pants.jvm.targets.java_thrift_library import JavaThriftLibrary
from pants.jvm.targets.jvm_binary import JvmApp, JvmBinary
from pants.jvm.targets.repository import Repository
from pants.jvm.targets.scala_library import ScalaLibrary
from pants.jvm.targets.scala_tests import ScalaTests
from pants.jvm.targets.scalac_plugin import ScalacPlugin
from pants.targets.dependencies import Dependencies
from pants.targets.doc import Page, Wiki
from pants.targets.resources import Resources

# aliases
target_aliases = {
  'annotation_processor': AnnotationProcessor,
  'benchmark': Benchmark,
  'credentials': Credentials,
  'dependencies': Dependencies,
  'jar_library': JarLibrary,
  'egg': PythonEgg,
  'java_agent': JavaAgent,
  'java_library': JavaLibrary,
  'java_antlr_library': JavaAntlrLibrary,
  'java_protobuf_library': JavaProtobufLibrary,
  'junit_tests': JavaTests,
  'java_tests': JavaTests,
  'java_thrift_library': JavaThriftLibrary,
  'jvm_binary': JvmBinary,
  'jvm_app': JvmApp,
  'page': Page,
  'python_binary': PythonBinary,
  'python_library': PythonLibrary,
  'python_requirement_library': PythonRequirementLibrary,
  'python_antlr_library': PythonAntlrLibrary,
  'python_thrift_library': PythonThriftLibrary,
  'python_tests': PythonTests,
  'python_test_suite': Dependencies,  # Legacy alias.
  'repo': Repository,
  'resources': Resources,
  'scala_library': ScalaLibrary,
  'scala_specs': ScalaTests,
  'scala_tests': ScalaTests,
  'scalac_plugin': ScalacPlugin,
  'wiki': Wiki,
}

from twitter.common.quantity import Amount, Time
from pants.goal import Goal, Group, Phase
from pants.jvm.targets.exclude import Exclude
from .build_environment import get_buildroot, get_version, get_scm, set_scm
from .config import Config

object_aliases = {
  'artifact': Artifact,
  'goal': Goal,
  'group': Group,
  'phase': Phase,
  'config': Config,
  'get_version': get_version,
  'get_buildroot': get_buildroot,
  'get_scm': get_scm,
  'set_scm': set_scm,
  'jar': JarDependency,
  'pants': lambda x: x,
  'python_requirement': PythonRequirement,
  'exclude': Exclude,
  'python_artifact': PythonArtifact,
  'setup_py': PythonArtifact,
  'Amount': Amount,
  'Time': Time,
}


from twitter.common.dirutil.fileset import Fileset
from pants.jvm.targets.jvm_binary import Bundle
from pants.base.source_root import SourceRoot
from pants.targets.python_requirements import python_requirements

def maven_layout(basedir='', rel_path=None):
  """Sets up typical maven project source roots for all built-in pants target types.

  Shortcut for ``source_root('src/main/java', *java targets*)``,
  ``source_root('src/main/python', *python targets*)``, ...

  :param string basedir: Instead of using this BUILD file's directory as
    the base of the source tree, use a subdirectory. E.g., instead of
    expecting to find java files in ``src/main/java``, expect them in
    ``**basedir**/src/main/java``.
  """

  def root(path, *types):
    SourceRoot.register(os.path.join(rel_path, basedir, path), *types)

  root('src/main/antlr', JavaAntlrLibrary, Page, PythonAntlrLibrary)
  root('src/main/java', AnnotationProcessor, JavaAgent, JavaLibrary, JvmBinary, Page)
  root('src/main/protobuf', JavaProtobufLibrary, Page)
  root('src/main/python', Page, PythonBinary, PythonLibrary)
  root('src/main/resources', Page, Resources)
  root('src/main/scala', JvmBinary, Page, ScalaLibrary)
  root('src/main/thrift', JavaThriftLibrary, Page, PythonThriftLibrary)

  root('src/test/java', JavaLibrary, JavaTests, Page)
  root('src/test/python', Page, PythonLibrary, PythonTests)
  root('src/test/resources', Page, Resources)
  root('src/test/scala', JavaTests, Page, ScalaLibrary, ScalaTests)


class FilesetRelPathWrapper(object):
  def __init__(self, rel_path):
    self.rel_path = rel_path

  def __call__(self, *args, **kwargs):
    root = os.path.join(get_buildroot(), self.rel_path)
    return self.wrapped_fn(root=root, *args, **kwargs)


class Globs(FilesetRelPathWrapper):
  wrapped_fn = Fileset.globs


class RGlobs(FilesetRelPathWrapper):
  wrapped_fn = Fileset.rglobs


class ZGlobs(FilesetRelPathWrapper):
  wrapped_fn = Fileset.zglobs


class BuildFilePath(object):
  def __init__(self, rel_path):
    self.rel_path = rel_path

  def __call__(self, *args, **kwargs):
    return os.path.join(get_buildroot(), self.rel_path)


applicative_path_relative_util_aliases = {
  'source_root': SourceRoot,
  'globs': Globs,
  'rglobs': RGlobs,
  'zglobs': ZGlobs,
  'buildfile_path': BuildFilePath,
}

partial_path_relative_util_aliases = {
  'maven_layout': maven_layout,
  'python_requirements': python_requirements,
  'bundle': Bundle,
}
