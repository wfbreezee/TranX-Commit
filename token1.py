
class Token(object):
    def __init__(self, value, type=None):
        self.value = value
        self.type = type

    def __repr__(self):
        if self.type is not None:
            return '%s(%s)' % (self.value, self.type)
        else:
            return self.value

class TokenSequence(list):
    def __init__(self, tokens=None):
        super(TokenSequence, self).__init__()
        if tokens is not None:
            self.extend(tokens)

    def __repr__(self):
        tokens = ", ".join([repr(token) for token in self])
        return "TokenSequence([%s])" % tokens