#!/usr/bin/env python3
"""
SlayScript Build Script - Cross-platform executable builder.
Uses PyInstaller to create standalone executables.
"""

import subprocess
import sys
import platform
import shutil
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"  {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
        return False
    return True


def main():
    print("=" * 50)
    print("  SlayScript Build Script")
    print("  Cast spells, slay bugs.")
    print("=" * 50)
    print()

    system = platform.system()
    print(f"Platform: {system}")
    print(f"Python: {sys.version}")
    print()

    # Determine executable name
    exe_name = "slayscript"
    if system == "Windows":
        exe_ext = ".exe"
        separator = ";"
        hidden_imports = [
            "--hidden-import=pyttsx3.drivers",
            "--hidden-import=pyttsx3.drivers.sapi5",
        ]
    elif system == "Darwin":
        exe_ext = ""
        separator = ":"
        hidden_imports = [
            "--hidden-import=pyttsx3.drivers",
            "--hidden-import=pyttsx3.drivers.nsss",
        ]
    else:  # Linux
        exe_ext = ""
        separator = ":"
        hidden_imports = [
            "--hidden-import=pyttsx3.drivers",
            "--hidden-import=pyttsx3.drivers.espeak",
        ]

    # Install dependencies
    print("Step 1: Installing dependencies")
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements"):
        print("Warning: Could not install requirements.txt dependencies")

    if not run_command(f"{sys.executable} -m pip install pyinstaller", "Installing PyInstaller"):
        print("Error: Failed to install PyInstaller")
        sys.exit(1)

    print()

    # Clean previous builds
    print("Step 2: Cleaning previous builds")
    for path in ["build", "dist", f"{exe_name}.spec"]:
        if Path(path).exists():
            if Path(path).is_dir():
                shutil.rmtree(path)
            else:
                Path(path).unlink()
            print(f"  Removed {path}")
    print()

    # Build executable
    print("Step 3: Building executable")

    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        f"--name={exe_name}",
        f"--add-data=slayscript{separator}slayscript",
        "--console",
        "--noconfirm",
    ] + hidden_imports + ["slayscript_cli.py"]

    print(f"  Running: {' '.join(pyinstaller_cmd)}")
    result = subprocess.run(pyinstaller_cmd)

    if result.returncode != 0:
        print()
        print("Error: Build failed")
        sys.exit(1)

    print()

    # Copy examples to dist
    print("Step 4: Copying examples to dist folder")
    dist_examples = Path("dist/examples")
    if dist_examples.exists():
        shutil.rmtree(dist_examples)
    shutil.copytree("examples", dist_examples)
    print(f"  Copied examples to {dist_examples}")
    print()

    # Success message
    exe_path = Path("dist") / f"{exe_name}{exe_ext}"
    print("=" * 50)
    print("  Build complete!")
    print(f"  Executable: {exe_path}")
    print("=" * 50)
    print()
    print("To run SlayScript:")
    if system == "Windows":
        print(f"  dist\\{exe_name}.exe examples\\hello_world.slay")
        print()
        print("To start the REPL:")
        print(f"  dist\\{exe_name}.exe")
    else:
        print(f"  ./dist/{exe_name} examples/hello_world.slay")
        print()
        print("To start the REPL:")
        print(f"  ./dist/{exe_name}")
    print()


if __name__ == "__main__":
    main()
