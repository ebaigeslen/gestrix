from app.auth.password import hash_password, verify_password


def test_hash_password_returns_different_value() -> None:
    assert hash_password("password123") != "password123"


def test_hash_password_nondeterministic() -> None:
    # bcrypt uses a random salt, so two hashes of the same plaintext differ.
    assert hash_password("password123") != hash_password("password123")


def test_verify_password_correct() -> None:
    hashed = hash_password("password123")
    assert verify_password("password123", hashed) is True


def test_verify_password_wrong() -> None:
    hashed = hash_password("password123")
    assert verify_password("wrong-password", hashed) is False


def test_verify_password_handles_garbage_hash() -> None:
    # A malformed hash must return False, never raise.
    assert verify_password("password123", "not-a-real-bcrypt-hash") is False
