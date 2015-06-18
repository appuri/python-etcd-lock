from pyvows import Vows

@Vows.create_assertions
def to_raise_error(topic, expected):
    ex = None
    try:
        topic()
    except Exception, e:
        ex = e

    return isinstance(ex, expected)
