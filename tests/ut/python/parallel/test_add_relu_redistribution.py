# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import numpy as np
from mindspore import context
import mindspore.nn as nn
from mindspore.ops import operations as P
from mindspore import Tensor
from tests.ut.python.ops.test_math_ops import VirtualLoss
import mindspore as ms
from mindspore.common.api import _executor
from mindspore.ops import composite as C


class AddRelu(nn.Cell):
    def __init__(self, strategy0=None, strategy1=None):
        super(AddRelu, self).__init__()
        self.add = P.TensorAdd().set_strategy(strategy=strategy0)
        self.relu = P.ReLU().set_strategy(strategy=strategy1)

    def construct(self, x, z):
        out = self.add(x, z)
        return self.relu(out)


class NetWithLoss(nn.Cell):
    def __init__(self, network):
        super(NetWithLoss, self).__init__()
        self.loss = VirtualLoss()
        self.network = network

    def construct(self, x, z):
        predict = self.network(x, z)
        return self.loss(predict)


class Grad(nn.Cell):
    def __init__(self, network):
        super(Grad, self).__init__()
        self.network = network

    def construct(self, x, y):
        return C.grad_all(self.network)(x, y)


def compile(net, x, y):
    net.set_auto_parallel()
    _executor.compile(net, x, y)


def test_add_relu_stride_slice():
    context.set_auto_parallel_context(device_num=8, global_rank=7)

    strategy0 = ((1, 1), (1, 1))
    strategy1 = ((8, 1),)
    net = Grad(NetWithLoss(AddRelu(strategy0, strategy1)))
    context.set_auto_parallel_context(parallel_mode="semi_auto_parallel")

    x = Tensor(np.ones([128, 32]), dtype=ms.float32)
    y = Tensor(np.ones([128, 32]), dtype=ms.float32)
    compile(net, x, y)


def test_add_relu_all_gather():
    context.set_auto_parallel_context(device_num=8, global_rank=7)

    strategy0 = ((8, 1), (8, 1))
    strategy1 = ((1, 1),)
    net = Grad(NetWithLoss(AddRelu(strategy0, strategy1)))
    context.set_auto_parallel_context(parallel_mode="semi_auto_parallel")

    x = Tensor(np.ones([128, 32]), dtype=ms.float32)
    y = Tensor(np.ones([128, 32]), dtype=ms.float32)
    compile(net, x, y)
