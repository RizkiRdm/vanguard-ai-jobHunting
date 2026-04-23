import pytest
from core.security import encrypt_credential, decrypt_credential, mask_email


def test_encryption_roundtrip():
    original_password = "password123_rahasia"
    encrypted = encrypt_credential(original_password)

    assert encrypted != original_password
    assert decrypt_credential(encrypted) == original_password


@pytest.mark.parametrize(
    "input_email, expected_output",
    [
        ("johndoe@example.com", "joh***e@example.com"),  # Standard
        ("ab@domain.com", "***@domain.com"),  # Short
        ("not_email", "not_email"),  # Invalid
        ("", ""),  # Empty
    ],
)
def test_mask_email_scenarios(input_email, expected_output):
    """Testing various email masking scenarios in one function."""
    assert mask_email(input_email) == expected_output


@pytest.mark.parametrize("empty_input", ["", None])
def test_encryption_empty_input(empty_input):
    """Ensuring that empty or None inputs are returned without modification."""
    encrypted = encrypt_credential(empty_input)
    decrypted = decrypt_credential(empty_input)

    assert encrypted == empty_input
    assert decrypted == empty_input

    # Additional data type checks for greater certainty
    assert type(encrypted) is type(empty_input)
