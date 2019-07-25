# Copyright 2018 The TensorFlow Probability Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Rough TensorFlow API implemented via JAX."""

from __future__ import absolute_import
from __future__ import division
# [internal] enable type annotations
from __future__ import print_function

import contextlib
import functools
import types

import jax
from jax import lax
import jax.numpy as np

__all__ = [
    'tf',
]

tf = types.ModuleType('tensorflow', '')


def _impl(path_in_tf=(), private=True, name=None):
  """Implements a TensorFlow function."""

  def _decorator(fn):
    """Implements a TensorFlow function."""
    cur_mod = tf
    for path_element in path_in_tf:
      if not hasattr(cur_mod, path_element):
        new_mod = types.ModuleType(path_element, '')
        setattr(cur_mod, path_element, new_mod)
      cur_mod = getattr(cur_mod, path_element)
    if name is None:
      if private:
        final_name = fn.__name__[1:]
      else:
        final_name = fn.__name__
    else:
      final_name = name
    setattr(cur_mod, final_name, fn)
    return fn

  return _decorator


_impl_np = functools.partial(_impl, private=False)


@_impl()
def _cond(pred, true_fn, false_fn):
  # TODO(siege): I'm not sure this is completely correct, does lax.cond
  # correctly handle closures?
  return lax.cond(pred, (), lambda _: true_fn(), (), lambda _: false_fn())


@_impl()
def _convert_to_tensor(value, dtype=None, name=None):
  del name
  return np.asarray(value, dtype)


@_impl()
def _while_loop(cond, body, loop_vars, **kwargs):  # pylint: disable=missing-docstring
  del kwargs

  # JAX doesn't do the automatic unwrapping of variables.
  def cond_wrapper(loop_vars):
    return cond(*loop_vars)

  def body_wrapper(loop_vars):
    return body(*loop_vars)

  return lax.while_loop(cond_wrapper, body_wrapper, loop_vars)


@_impl()
class _TensorSpec(object):
  pass


@_impl(name='cast')
def _cast(v, dtype):
  return np.asarray(v).astype(dtype)


@_impl()
@contextlib.contextmanager
def _name_scope(name):
  yield name


@_impl()
def _rank(x):
  # JAX doesn't have rank implemented.
  return len(x.shape)


@_impl()
def _function(x):
  return jax.jit(x)


_impl(name='add_n')(sum)

_impl_np()(np.float32)
_impl_np()(np.int32)
_impl_np()(np.ones)
_impl_np()(np.reshape)
_impl_np()(np.shape)
_impl_np()(np.where)
_impl_np()(np.zeros)
_impl_np()(np.zeros_like)
_impl_np(['math'])(np.log)
_impl_np(['math'])(np.sqrt)
_impl_np(['math'], name='pow')(np.power)
_impl_np(['math'], name='reduce_variance')(np.var)
_impl_np(name='abs')(np.abs)
_impl_np(name='Tensor')(np.ndarray)
_impl_np(name='concat')(np.concatenate)
_impl_np(name='constant')(np.array)
_impl_np(name='range')(np.arange)
_impl_np(name='reduce_max')(np.max)
_impl_np(name='reduce_mean')(np.mean)
_impl_np(name='reduce_sum')(np.sum)
_impl_np(name='square')(np.square)
