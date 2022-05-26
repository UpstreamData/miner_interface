from miners import BaseMiner


class M21(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M21"
        self.nominal_chips = 105
        self.fan_count = 2
