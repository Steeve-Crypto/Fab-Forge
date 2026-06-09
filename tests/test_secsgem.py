"""Tests for the SECS/GEM emulator layer."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fabforge.secsgem_layer import SECSGEMEmulator


def test_secsgem_basic_flow():
    gem = SECSGEMEmulator()
    gem.process_command("START", 99)
    assert gem.equipment_status == "PROCESSING"
    gem.send_stream(1, 1, {"equipment": "LithoTool"})
    # Just ensure it doesn't crash and increments
    assert gem.wafer_count >= 1


def test_secsgem_stop():
    gem = SECSGEMEmulator()
    gem.process_command("START", 1)
    gem.process_command("STOP", 1)
    assert gem.equipment_status == "IDLE"