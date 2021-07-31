from json import JSONEncoder


class Config:
    weight: str
    label: str
    threshold: float
    version: int

    def __init__(self, weight, label, threshold, version):
        self.weight = weight
        self.label = label
        self.threshold = threshold
        self.version = version


class ConfigEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
