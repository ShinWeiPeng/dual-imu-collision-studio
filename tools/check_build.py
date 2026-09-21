import hashlib
import pathlib
import subprocess
import sys

def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    venv_py = root / ".venv" / "Scripts" / "python.exe"
    toml_file = root / "pyproject.toml"
    hash_file = root / ".venv" / ".pyproject.hash"

    if not toml_file.exists():
        return

    current_hash = hashlib.sha256(toml_file.read_bytes()).hexdigest()
    stored_hash = hash_file.read_text().strip() if hash_file.exists() else ""

    if current_hash != stored_hash:
        print("[資訊] 檢測到 pyproject.toml 變更，正在執行 pip install -e . ...")
        res = subprocess.run([str(venv_py), "-m", "pip", "install", "-e", "."])
        if res.returncode == 0:
            hash_file.parent.mkdir(parents=True, exist_ok=True)
            hash_file.write_text(current_hash)
        else:
            sys.exit(res.returncode)

if __name__ == "__main__":
    main()
