from .payload import Payload, PayloadType


class SuccessPayload(Payload):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return "Success"

    @property
    def type(self):
        return PayloadType.SUCCESS

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return None


class NotImplementedPayload(Payload):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return "Not implemented"

    @property
    def type(self):
        return PayloadType.NOT_IMPLEMENTED

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return None


class FailurePayload(Payload):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return "Failure"

    @property
    def type(self):
        return PayloadType.FAILURE

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return None


class InvalidRequestPayload(Payload):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return "Invalid request"

    @property
    def type(self):
        return PayloadType.INVALID_REQUEST

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return None
