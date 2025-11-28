#!/usr/bin/env python3
import subprocess
import pkg_resources

IGNORE_PREFIXES = [
    "torch",
    "torchaudio",
    "torchvision",
    "triton",
    "nvidia-",
]

IGNORE_EXACT = {
    "pip",
    "setuptools",
    "wheel",
}

REFERENCE_FILE = "reference.txt"

def load_reference():
    ref = {}
    with open(REFERENCE_FILE) as f:
        for line in f:
            line = line.strip()
            if "==" not in line:
                continue
            pkg, ver = line.split("==")
            pkg = pkg.lower()

            # skip ignored packages in reference
            if pkg in IGNORE_EXACT or any(pkg.startswith(p) for p in IGNORE_PREFIXES):
                continue

            ref[pkg] = ver
    return ref

def get_current():
    cur = {}
    for dist in pkg_resources.working_set:
        pkg = dist.project_name.lower()

        if pkg in IGNORE_EXACT or any(pkg.startswith(p) for p in IGNORE_PREFIXES):
            continue

        cur[pkg] = dist.version
    return cur

def main():
    print("🔍 Loading reference...")
    ref = load_reference()
    cur = get_current()

    # ========== INSTALL / UPGRADE / DOWNGRADE ==========
    for pkg, ver in ref.items():
        if pkg not in cur:
            print(f"📦 Installing missing: {pkg}=={ver}")
            subprocess.run(["pip", "install", f"{pkg}=={ver}"])
        elif cur[pkg] != ver:
            print(f"🔄 Version mismatch: {pkg} {cur[pkg]} → {ver}")
            subprocess.run(["pip", "install", "--force-reinstall", f"{pkg}=={ver}"])

    # ========== REMOVE PACKAGES NOT IN REFERENCE ==========
    for pkg in cur:
        if pkg not in ref:
            print(f"❌ Extra package found (not in reference): {pkg}")
            # To actually remove it, uncomment:
            # subprocess.run(["pip", "uninstall", "-y", pkg])

    print("✅ Sync complete")

if __name__ == "__main__":
    main()
