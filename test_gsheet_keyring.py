import pytest
import keyring


class MockKeyringBackend(keyring.KeyringBackend):
    _passwords = dict()

    # def get_password


@pytest.fixture
def keyring_backend():
    saved_backend = keyring.get_keyring()
    try:
        keyring.set_keyring(MockKeyringBackend())
        yield
    finally:
        keyring.set_keyring(saved_backend)


def test(keyring_backend):
    assert not keyring.get_keyring()
