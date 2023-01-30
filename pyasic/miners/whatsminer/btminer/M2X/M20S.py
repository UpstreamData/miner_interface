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

from pyasic.miners._backends import BTMiner  # noqa - Ignore access to _module
from pyasic.miners._types import (  # noqa - Ignore access to _module
    M20SV10,
    M20SV20,
    M20SV30,
)


class BTMinerM20SV10(BTMiner, M20SV10):
    pass


class BTMinerM20SV20(BTMiner, M20SV20):
    pass


class BTMinerM20SV30(BTMiner, M20SV30):
    pass
