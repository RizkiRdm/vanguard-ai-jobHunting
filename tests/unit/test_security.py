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
        ("johndoe@example.com", "joh***@example.com"),  # Standard
        ("ab@domain.com", "ab***@domain.com"),  # Short
        ("not_email", "not_email"),  # Invalid
        ("", ""),  # Empty
    ],
)
def test_mask_email_scenarios(input_email, expected_output):
    """Mengetes berbagai skenario masking email dalam satu fungsi."""
    assert mask_email(input_email) == expected_output


@pytest.mark.parametrize("empty_input", ["", None])
def test_encryption_empty_input(empty_input):
    """Memastikan input kosong atau None dikembalikan apa adanya."""
    encrypted = encrypt_credential(empty_input)
    decrypted = decrypt_credential(empty_input)

    assert encrypted == empty_input
    assert decrypted == empty_input

    # Tambahan pengecekan tipe data agar lebih pasti
    assert type(encrypted) is type(empty_input)
