class Board:

    def __init__(self, title, id=None):
        if not title:
            raise ValidationError("invalid title")

        self.id = id
        self.title = title


class ValidationError(Exception):
    pass
