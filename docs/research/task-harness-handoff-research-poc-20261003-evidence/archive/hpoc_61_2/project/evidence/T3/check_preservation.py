from pathlib import Path
import hashlib

expected = {
    "check.py": "a56704199f07a47bcd050adbb187f7eb072e02b2693d7afaa7fecc57b27fcc14",
    "other-plan.md": "387b9111d8d8567adb8ef7522374cd11b8b29dbc38e44e38f470fd011a6eb5b0",
    "user-note.txt": "dc25b33f923d36c38694095e76fee4b6709b67804f5e85c6aa9dd88f5be8f552",
    "project-setting.md": "d26b8e41c395dbe0080550bd8dc8b0d1fa74babd113cc5b61a12f272761a39d1",
}
for name, digest in expected.items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest, name
print("PASS read-only fixture fingerprints preserved")
