from default_serializer import DefaultSerializer


class ClientOptions:
    def __init__(self):
        self.serializer = DefaultSerializer()
        self.processor = lambda m, n: n.proceed(m)
        self.use_binary = False
        self.timeout_ms = 5000

    def set_serializer(self, serializer):
        self.serializer = serializer
        return self

    def set_processor(self, processor):
        self.processor = processor
        return self

    def set_use_binary(self, use_binary):
        self.use_binary = use_binary
        return self

    def set_timeout_ms(self, timeout_ms):
        self.timeout_ms = timeout_ms
        return self
