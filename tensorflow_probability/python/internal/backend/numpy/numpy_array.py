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
"""Numpy implementations of TensorFlow general top-level functions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Dependency imports
import numpy as np

import tensorflow as tf

from tensorflow_probability.python.internal.backend.numpy.internal import utils
from tensorflow_probability.python.internal.backend.numpy.linalg import norm


__all__ = [
    'concat',
    'expand_dims',
    'fill',
    'gather',
    'gather_nd',
    'linspace',
    'meshgrid',
    'norm',
    'one_hot',
    'ones',
    'ones_like',
    'pad',
    'range',
    'rank',
    'reshape',
    'reverse',
    'roll',
    'searchsorted',
    'shape',
    'size',
    'slice',
    'split',
    'squeeze',
    'stack',
    'tile',
    'transpose',
    'unstack',
    'where',
    'zeros',
    'zeros_like',
    # 'boolean_mask',
    # 'einsum',
    # 'foldl',
    # 'foldr',
    # 'tensordot',
]


# TODO(b/256095991): Add unit test.
def _gather(  # pylint: disable=unused-argument
    params,
    indices,
    validate_indices=None,
    axis=None,
    batch_dims=0,
    name=None):
  """gather."""
  if validate_indices is not None:
    raise NotImplementedError(
        'Argument `validate_indices != None` is currently unimplemented.')
  if batch_dims != 0:
    raise NotImplementedError(
        'Argument `batch_dims != 0` is currently unimplemented.')
  return np.take(params, indices, axis=axis)


def _gather_nd(  # pylint: disable=unused-argument
    params,
    indices,
    batch_dims=0,
    name=None):
  """gather_nd."""
  raise NotImplementedError


def _one_hot(  # pylint: disable=unused-argument
    indices,
    depth,
    on_value=None,
    off_value=None,
    axis=None,
    dtype=None,
    name=None):
  """One hot."""
  if on_value is None:
    on_value = 1
  if off_value is None:
    off_value = 0
  if axis is None:
    axis = -1

  zeros = np.zeros_like(indices)  # pylint: disable=redefined-outer-name
  zeros = np.tile(zeros[..., None], [1] * len(indices.shape) + [depth])

  ones = np.ones_like(zeros)  # pylint: disable=redefined-outer-name

  cond = np.abs(np.arange(depth, dtype=np.float32)[None] + zeros
                - indices[..., None] + zeros) < 0.1

  y_out = np.where(cond, ones * on_value, zeros + off_value)

  if axis is not None:
    y_out = np.swapaxes(y_out, axis, -1)

  return y_out


def _ones_like(input, dtype=None, name=None):  # pylint: disable=redefined-builtin
  s = _shape(input)
  if isinstance(s, (np.ndarray, np.generic)):
    return np.ones(s, utils.numpy_dtype(dtype or input.dtype))
  return tf.ones(s, dtype or s.dtype, name)


# TODO(b/136555907): Add unit-test.
def _pad(  # pylint: disable=unused-argument
    tensor,
    paddings,
    mode='CONSTANT',
    constant_values=0,
    name=None):
  return np.pad(
      tensor, paddings,
      mode=mode.lower(),
      constant_values=constant_values)


def _reverse(tensor, axis, name=None):  # pylint: disable=unused-argument
  if np.array(axis).ndim == 0:
    return np.flip(tensor, axis)
  for ax in axis:
    tensor = np.flip(tensor, ax)
  return tensor


def _searchsorted(  # pylint: disable=unused-argument
    sorted_sequence,
    values,
    side='left',
    out_type=tf.int32,
    name=None):
  return np.searchsorted(
      sorted_sequence, values, side=side, sorter=None).astype(out_type)


def _shape(input, out_type=tf.int32, name=None):  # pylint: disable=redefined-builtin,unused-argument
  return np.array(np.array(input).shape).astype(utils.numpy_dtype(out_type))


def _size(input, out_type=tf.int32, name=None):  # pylint: disable=redefined-builtin, unused-argument
  return np.prod(np.array(input).shape).astype(utils.numpy_dtype(out_type))


builtin_slice = slice  # pylint: disable=invalid-name


def _slice(input_, begin, size, name=None):  # pylint: disable=unused-argument,redefined-outer-name
  slices = tuple(
      builtin_slice(b, b + s if s != -1 else -1) for b, s in zip(begin, size))
  return input_[slices]


def _split(value, num_or_size_splits, axis=0, num=None, name='split'):  # pylint: disable=unused-argument
  """Map tf.split -> np.split."""
  indices_or_sections = num_or_size_splits
  if np.array(indices_or_sections).ndim == 1:
    if any(idx == -1 for idx in indices_or_sections):
      # Numpy parameterizes by split indices and returns nsplits+1 arrays.
      total_splits = sum(idx for idx in indices_or_sections if idx != -1)
      remainder = max(0, np.array(value).shape[axis] - total_splits)
      indices_or_sections = [
          idx if idx != -1 else remainder for idx in indices_or_sections
      ]
    indices_or_sections = np.cumsum(indices_or_sections)[:-1]
  return np.split(value, indices_or_sections, axis)


def _transpose(a, perm=None, conjugate=False, name='transpose'):  # pylint: disable=unused-argument
  x = np.transpose(a, perm)
  return np.conjugate(x) if conjugate else x


def _zeros_like(input, dtype=None, name=None):  # pylint: disable=redefined-builtin
  s = _shape(input)
  if isinstance(s, (np.ndarray, np.generic)):
    return np.zeros(s, utils.numpy_dtype(dtype or input.dtype))
  return tf.zeros(s, dtype or s.dtype, name)


# --- Begin Public Functions --------------------------------------------------


concat = utils.copy_docstring(
    tf.concat,
    lambda values, axis, name='concat': np.concatenate(values, axis))

expand_dims = utils.copy_docstring(
    tf.expand_dims,
    lambda input, axis, name=None: np.expand_dims(input, axis))

fill = utils.copy_docstring(
    tf.fill,
    lambda dims, value, name=None: value * np.ones(dims, np.array(value).dtype))

gather = utils.copy_docstring(
    tf.gather,
    _gather)

gather_nd = utils.copy_docstring(
    tf.gather_nd,
    _gather_nd)

reverse = utils.copy_docstring(tf.reverse, _reverse)

linspace = utils.copy_docstring(
    tf.linspace,
    lambda start, stop, num, name=None: (  # pylint: disable=g-long-lambda
        np.linspace(start, stop, num).astype(np.array(start).dtype)))

meshgrid = utils.copy_docstring(
    tf.meshgrid,
    np.meshgrid)

norm = utils.copy_docstring(
    tf.norm,
    norm)

one_hot = utils.copy_docstring(
    tf.one_hot,
    _one_hot)

ones = utils.copy_docstring(
    tf.ones,
    lambda shape, dtype=tf.float32, name=None: np.ones(  # pylint: disable=g-long-lambda
        shape, utils.numpy_dtype(dtype)))

ones_like = utils.copy_docstring(
    tf.ones_like,
    _ones_like)

pad = utils.copy_docstring(
    tf.pad,
    _pad)

range = utils.copy_docstring(  # pylint: disable=redefined-builtin
    tf.range,
    lambda start, limit=None, delta=1, dtype=None, name='range': (  # pylint: disable=g-long-lambda
        np.arange(start, limit, delta, utils.numpy_dtype(dtype))))

rank = utils.copy_docstring(
    tf.rank,
    lambda input, name=None: len(np.array(input).shape))  # pylint: disable=redefined-builtin,g-long-lambda

reshape = utils.copy_docstring(
    tf.reshape,
    lambda tensor, shape, name=None: np.reshape(tensor, shape))

roll = utils.copy_docstring(
    tf.roll,
    lambda input, shift, axis: np.roll(input, shift, axis))  # pylint: disable=unnecessary-lambda

searchsorted = utils.copy_docstring(
    tf.searchsorted,
    _searchsorted)

shape = utils.copy_docstring(
    tf.shape,
    _shape)

size = utils.copy_docstring(
    tf.size,
    _size)

slice = utils.copy_docstring(  # pylint: disable=redefined-builtin
    tf.slice, _slice)

split = utils.copy_docstring(tf.split, _split)

squeeze = utils.copy_docstring(
    tf.squeeze,
    lambda input, axis=None, name=None: np.squeeze(input, axis))

stack = utils.copy_docstring(
    tf.stack, lambda values, axis=0, name=None: np.stack(values, axis))

tile = utils.copy_docstring(
    tf.tile,
    lambda input, multiples, name=None: np.tile(input, multiples))

transpose = utils.copy_docstring(
    tf.transpose,
    _transpose)

unstack = utils.copy_docstring(
    tf.unstack,
    lambda value, num=None, axis=0, name=None: np.split(value, num, axis))

where = utils.copy_docstring(
    tf.compat.v1.where,
    lambda condition, x=None, y=None, name=None: np.where(condition, x, y))

zeros = utils.copy_docstring(
    tf.zeros,
    lambda shape, dtype=tf.float32, name=None: np.zeros(  # pylint: disable=g-long-lambda
        shape, utils.numpy_dtype(dtype)))

zeros_like = utils.copy_docstring(
    tf.zeros_like,
    _zeros_like)
