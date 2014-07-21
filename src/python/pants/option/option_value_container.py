# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from pants.option.parser_hierarchy import RankedValue


class OptionValueContainer(object):
  """A container for option values.

  Implements the following functionality:

  1) Attribute forwarding.

     An attribute can be registered as forwarding to another attribute, and attempts
     to read the source attribute's value will be read from the target attribute.

     This is necessary so we can qualify registered options by the scope that registered them,
     to allow re-registration in inner scopes. This is best explained by example:

     Say that in global scope we register an option with two names: [-f, --foo], which writes its
     value to the attribute foo. Then in scope compile we re-register --foo but leave -f alone.
     The re-registered --foo will also write to attribute foo. So now -f, which in the compile
     scope is unrelated to --foo, can still stomp on its value.

     With attribute forwarding we can have the global scope option write to _DEFAULT_foo__, and
     the re-registered option to _COMPILE_foo__, and then have the 'f' and 'foo' attributes
     forward, appropriately.

     Note that if the source attribute is set directly, this overrides any forwarding.

  2) Value ranking.

     Attribute values can be ranked, so that a given attribute's value can only be changed if
     the new value has at least as high a rank as the old value. This allows an option value in
     an outer scope to override that option's value in an inner scope, when the outer scope's
     value comes from a higher ranked source (e.g., the outer value comes from an env var and
     the inner one from config).

     See RankedValue for more details.

  Note that this container is suitable for passing as the namespace argument to argparse's
  parse_args() method.
  """
  def __init__(self):
    self._forwardings = {}  # src attribute name -> target attribute name.

  def add_forwardings(self, forwardings):
    self._forwardings.update(forwardings)

  def update(self, attrs):
    """Set attr values on this object from the data in the attrs dict."""
    for k, v in attrs.items():
      setattr(self, k, v)

  def __setattr__(self, key, value):
    if hasattr(self, key):
      existing_value = getattr(self, key)
      if isinstance(existing_value, RankedValue):
        existing_rank = existing_value.rank
      else:
        # Values without rank are assumed to be flag values set by parse_args().
        existing_rank = RankedValue.FLAG
    else:
      existing_rank = RankedValue.NONE

    if isinstance(value, RankedValue):
      new_rank = value.rank
    else:
      # Values without rank are assumed to be flag values set by parse_args().
      new_rank = RankedValue.FLAG

    if new_rank >= existing_rank:
      super(OptionValueContainer, self).__setattr__(key, value)

  def __getattr__(self, key):
    # Note: Called only if regular attribute lookup fails, so accesses
    # to non-forwarded attributes will be handled as usual.
    if key not in self._forwardings:
      raise AttributeError('No such forwarded attribute: %s' % key)
    val = getattr(self, self._forwardings[key])
    if isinstance(val, RankedValue):
      return val.value
    else:
      return val
