import robber

class Raise(robber.matchers.base.Base):
    def matches(self):
        ex = None
        try:
            self.actual()
        except Exception, e:
            ex = e
        self.ex = ex
        return isinstance(ex, self.expected)

    def failure_message(self):
        return 'Expected lamba to raise error "%s", but raised "%s"' % (self.expected, self.ex)

robber.expect.register('raise_error', Raise)

# @Vows.create_assertions
# def to_raise_error(topic, expected):
#     ex = None
#     try:
#         topic()
#     except Exception, e:
#         ex = e

#     return isinstance(ex, expected)
