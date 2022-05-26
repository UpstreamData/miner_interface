from miners._backends import BMMiner  # noqa - Ignore access to _module
from miners._types import T17Plus  # noqa - Ignore access to _module


class BMMinerT17Plus(BMMiner, T17Plus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
