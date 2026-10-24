import json
from pathlib import Path

def test_identity_points_to_generated_icons():
    root = Path(__file__).resolve().parents[2] / 'mobile'
    config = json.loads((root/'app.json').read_text())['expo']
    assert config['name'] == 'ZINC'
    assert config['ios']['bundleIdentifier'] == 'com.zinc.coach'
    assert (root/config['icon']).is_file()
    png = (root/config['icon']).read_bytes()
    assert png[:8] == b'\x89PNG\r\n\x1a\n'
    assert int.from_bytes(png[16:20],'big') == 1024
    assert int.from_bytes(png[20:24],'big') == 1024
