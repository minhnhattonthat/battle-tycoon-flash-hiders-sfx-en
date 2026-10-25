import hashlib


def test_rom_matches_pin(rom):
    assert hashlib.sha1(rom).hexdigest() == "1959552f9f18335d9e1afb2c98763511fffd1be8"
