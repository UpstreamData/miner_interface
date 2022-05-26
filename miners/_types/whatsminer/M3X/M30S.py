from miners import BaseMiner


class M30S(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M30S"
        # TODO: Add chip count for this miner (per board) - self.nominal_chips
        self.fan_count = 2
