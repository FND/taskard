class Board:

    def __init__(self, title):
        if not title:
            raise ValidationError("invalid title")

        self.title = title


class ValidationError(Exception):
    pass
