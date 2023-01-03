#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from pyasic.miners._types.makes import WhatsMiner


class M31SPlus(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+"
        self.nominal_chips = 78
        self.fan_count = 2


class M31SPlusVE20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ VE20"
        self.nominal_chips = 78
        self.fan_count = 2


class M31SPlusV30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V30"
        self.nominal_chips = 117
        self.fan_count = 2


class M31SPlusV40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V40"
        self.nominal_chips = 123
        self.fan_count = 2


class M31SPlusV60(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V60"
        self.nominal_chips = 156
        self.fan_count = 2


class M31SPlusV80(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V80"
        self.nominal_chips = 129
        self.fan_count = 2


class M31SPlusV90(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V90"
        self.nominal_chips = 117
        self.fan_count = 2
