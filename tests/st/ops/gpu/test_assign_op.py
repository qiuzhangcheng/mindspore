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
# ============================================================================

import pytest
from mindspore import Tensor, Parameter
from mindspore.ops import operations as P
import mindspore.nn as nn
import numpy as np
import mindspore.context as context


class Net(nn.Cell):
    def __init__(self, value):
        super(Net, self).__init__()
        self.var = Parameter(value, name="var")
        self.assign = P.Assign()

    def construct(self, value):
        return self.assign(self.var, value)


x = np.array([[1.2, 1], [1, 0]]).astype(np.float32)
value = np.array([[1, 2], [3, 4.0]]).astype(np.float32)


@pytest.mark.level0
@pytest.mark.platform_x86_gpu_training
@pytest.mark.env_onecard
def test_assign():
    context.set_context(mode=context.GRAPH_MODE, device_target="GPU")
    var = Tensor(x)
    assign = Net(var)
    output = assign(Tensor(value))

    error = np.ones(shape=[2, 2]) * 1.0e-6
    diff1 = output.asnumpy() - value
    diff2 = assign.var.default_input.asnumpy() - value
    assert np.all(diff1 < error)
    assert np.all(-diff1 < error)
    assert np.all(diff2 < error)
    assert np.all(-diff2 < error)
