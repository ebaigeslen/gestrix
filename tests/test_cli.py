from gestrix.cli import hello


def test_hello_default():
    assert hello() == "Hello, world!"


def test_hello_name():
    assert hello("Gestrix") == "Hello, Gestrix!"
