from pathlib import Path
import hashlib, json
root = Path(__file__).resolve().parents[1]
manifest = json.loads((root/"manifest.json").read_text())
for row in manifest["files"]:
    path = (root/row["path"]).resolve()
    assert path.is_relative_to(root), "Unsafe manifest path"
    data = path.read_bytes()
    assert len(data) == row["bytes"], row["path"]
    assert hashlib.sha256(data).hexdigest() == row["sha256"], row["path"]
print(f"Verified {len(manifest['files'])} files")
