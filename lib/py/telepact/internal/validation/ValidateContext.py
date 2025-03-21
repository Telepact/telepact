class ValidateContext:
    select: dict[str, object] | None
    fn: str | None

    def __init__(self, select: dict[str, object] | None = None, fn: str | None = None):
        self.select = select
        self.fn = fn
