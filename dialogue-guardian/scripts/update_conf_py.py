# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
import sys
import re

def update_conf_py(new_version):
    conf_py_path = "docs/conf.py"
    
    with open(conf_py_path, "r") as f:
        content = f.read()

    # Replace release = 'X.Y.Z' or release = "X.Y.Z" or release = X.Y.Z
    content = re.sub(r"release = ['\"]?[0-9]+\.[0-9]+\.[0-9]+['\"]?", f"release = '{new_version}'", content)
    
    # Replace version = 'X.Y.Z' or version = "X.Y.Z" or version = X.Y.Z
    content = re.sub(r"version = ['\"]?[0-9]+\.[0-9]+\.[0-9]+['\"]?", f"version = '{new_version}'", content)

    with open(conf_py_path, "w") as f:
        f.write(content)
    
    print(f"Updated docs/conf.py with version {new_version}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_conf_py.py <new_version>")
        sys.exit(1)
    
    new_version = sys.argv[1]
    update_conf_py(new_version)