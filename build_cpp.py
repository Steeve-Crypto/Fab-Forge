#!/usr/bin/env python3
"""
FabForge C++ build helper for Windows (and Unix).

This script uses the pip-installed 'cmake' module (python -m cmake)
so you don't need cmake in your global PATH.

Prerequisites on Windows:
  - Visual Studio 2022 (or Build Tools) with "Desktop development with C++" workload installed.
  - Then run this from an "x64 Native Tools Command Prompt for VS 2022"
    (or "Developer Command Prompt for Visual Studio").
  - Python 3.8+ (the same one you use for the project, preferably 64-bit).

Usage:
  python build_cpp.py

On success you will get:
  - fab_sim.exe (or fab_sim on Unix) in the project root
  - fabforge_cpp.pyd / .so  (the PyBind11 module) placed so that
    "import fabforge_cpp" works when running the fabforge package from source.

If the compiler is not found you will get a clear message with what to install.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
BUILD_DIR = ROOT / "build-win" if os.name == "nt" else ROOT / "build"
FAB_SIM_NAME = "fab_sim.exe" if os.name == "nt" else "fab_sim"
PYD_GLOB = "fabforge_cpp*.pyd" if os.name == "nt" else "fabforge_cpp*.so"

def find_cmake():
    # Prefer the one from pip 'cmake' package
    try:
        import cmake
        cmake_exe = Path(cmake.CMAKE_BIN_DIR) / "cmake.exe" if os.name == "nt" else Path(cmake.CMAKE_BIN_DIR) / "cmake"
        if cmake_exe.exists():
            return str(cmake_exe)
    except Exception:
        pass

    # Fallback to PATH
    cmake_cmd = shutil.which("cmake")
    if cmake_cmd:
        return cmake_cmd

    # Last resort: python -m cmake (the module registers entry point)
    return [sys.executable, "-m", "cmake"]

def run(cmd, cwd=None, env=None):
    print(f"$ {' '.join(cmd) if isinstance(cmd, (list, tuple)) else cmd}")
    p = subprocess.run(cmd, cwd=cwd, env=env, shell=False, capture_output=False)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed with code {p.returncode}")
    return p

def main():
    print("=== FabForge C++ Native Build (Windows-friendly) ===")
    print(f"Project root: {ROOT}")
    print(f"Target build dir: {BUILD_DIR}")

    cmake_cmd = find_cmake()
    print(f"Using CMake: {cmake_cmd}")

    # Ensure build dir
    BUILD_DIR.mkdir(exist_ok=True)

    # Configure
    # Help CMake find the pybind11 we pip-installed (critical on Windows)
    pybind11_cmake_dir = None
    try:
        import pybind11
        pybind11_cmake_dir = pybind11.get_cmake_dir()
    except Exception:
        pass

    configure_args = [
        *([cmake_cmd] if isinstance(cmake_cmd, str) else cmake_cmd),
        "-S", str(ROOT),
        "-B", str(BUILD_DIR),
        "-DCMAKE_BUILD_TYPE=Release",
    ]
    if pybind11_cmake_dir:
        configure_args += [f"-Dpybind11_DIR={pybind11_cmake_dir}"]
    # On Windows, let CMake pick the generator (it will look for VS when run from dev prompt)
    # You can force: -G "Visual Studio 17 2022" -A x64

    try:
        run(configure_args)
    except Exception as e:
        print("\n" + "="*60)
        print("CONFIGURE FAILED — likely missing C++ compiler / Visual Studio.")
        print("="*60)
        print("""
On Windows you need:

1. Download & install "Build Tools for Visual Studio 2022" (free) from Microsoft:
   https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022

   OR the full Visual Studio with the workload:
   "Desktop development with C++"

2. After install, open the **x64 Native Tools Command Prompt for VS 2022**
   (search Start menu for "Native Tools").

3. In that prompt, cd to this folder and run again:
   python build_cpp.py

Alternative (if you have cl.exe somewhere):
   set PATH=...\\VC\\Tools\\MSVC\\...\\bin\\Hostx64\\x64;%PATH%
   python build_cpp.py
""")
        sys.exit(1)

    # Build
    build_args = [
        *([cmake_cmd] if isinstance(cmake_cmd, str) else cmake_cmd),
        "--build", str(BUILD_DIR),
        "--config", "Release",
        "--parallel",
    ]
    run(build_args)

    # Locate artifacts
    print("\n=== Locating build artifacts ===")

    # fab_sim
    candidates = list(BUILD_DIR.rglob("fab_sim*")) + list(BUILD_DIR.rglob("fab_sim.exe"))
    fab_sim_src = None
    for c in candidates:
        if c.is_file() and "fab_sim" in c.name and not c.name.endswith(".pdb"):
            fab_sim_src = c
            break

    if fab_sim_src:
        dst = ROOT / FAB_SIM_NAME
        shutil.copy2(fab_sim_src, dst)
        print(f"Copied fab_sim -> {dst}")
    else:
        print("WARNING: Could not find built fab_sim executable.")

    # PyBind11 module (.pyd or .so)
    pyd_candidates = list(BUILD_DIR.rglob(PYD_GLOB)) + list(BUILD_DIR.rglob("fabforge_cpp*"))
    pyd_src = None
    for c in pyd_candidates:
        if c.is_file() and ("fabforge_cpp" in c.name) and (c.suffix in (".pyd", ".so", ".dll")):
            pyd_src = c
            break

    if pyd_src:
        # Place it next to the fabforge package so "import fabforge_cpp" works from source tree
        dst = ROOT / "fabforge" / pyd_src.name
        shutil.copy2(pyd_src, dst)
        print(f"Copied PyBind11 module -> {dst}")
        print("You can now do:  python -c \"import fabforge_cpp; print('Native core available')\"")
    else:
        print("WARNING: Could not find built fabforge_cpp module (pyd/so).")

    print("\n✅ Build complete (or artifacts copied).")
    print("The Python fallback in CLI + backend will still work if native is not importable.")
    print("To use native in simulate: python -m fabforge.cli simulate --use-cpp")

if __name__ == "__main__":
    main()