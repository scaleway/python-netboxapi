class ForbiddenAsChildError(Exception):
    pass


class ForbiddenAsPassiveMapperError(Exception):
    def __init__(self):
        super().__init__("No action is possible for this type of mapper")
