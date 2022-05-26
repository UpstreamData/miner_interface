from miners._backends import BMMiner  # noqa - Ignore access to _module
from miners._types import T17  # noqa - Ignore access to _module


class BMMinerT17(BMMiner, T17):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
