import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "Battle Tycoon - Flash Hiders SFX (Japan) (Rev 1).sfc"


@pytest.fixture
def rom():
    if not ROM.is_file():
        pytest.skip("original ROM absent")
    return ROM.read_bytes()
