#!/usr/bin/env python
"""
Cross-platform build script for GWM Fortran extensions.

This script provides an alternative to setup.py for building Fortran extensions
and can be run directly or integrated into setup.py.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path


def check_fortran_compiler():
    """Check if a Fortran compiler is available"""
    compilers = {
        'Linux': ['gfortran', 'f77', 'f90'],
        'Darwin': ['gfortran', 'f77', 'f90'],  # macOS
        'Windows': ['gfortran', 'f77', 'f90', 'ifort'],
    }
    
    system = platform.system()
    compiler_list = compilers.get(system, ['gfortran', 'f77', 'f90'])
    
    for compiler in compiler_list:
        try:
            result = subprocess.run(
                [compiler, '--version'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✓ Found Fortran compiler: {compiler}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    return False


def check_f2py():
    """Check if f2py is available"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "numpy.f2py", "-v"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ f2py (numpy.f2py) is available")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False


def install_dependencies():
    """Install required Python dependencies"""
    print("\n" + "="*70)
    print("Installing Python dependencies...")
    print("="*70)
    
    dependencies = [
        "numpy~=1.26.4",
        "scipy~=1.13.1",
        "matplotlib~=3.9.2",
        "PyQt5~=5.15.10",
        "pillow~=10.4.0",
    ]
    
    cmd = [sys.executable, "-m", "pip", "install"] + dependencies
    result = subprocess.run(cmd)
    return result.returncode == 0


def build_fortran_extension(module_name, source_files, extra_flags=None):
    """Build a single Fortran extension with f2py"""
    if extra_flags is None:
        extra_flags = []
    
    # Prepare command
    cmd = [
        sys.executable, "-m", "numpy.f2py",
        "-c",
        "-m", module_name,
    ]
    
    # Add compiler selection for Windows
    system = platform.system()
    if system == "Windows":
        cmd.extend(["--compiler=mingw32", "--fcompiler=gnu95"])
    else:
        # For Linux/Mac, let f2py auto-detect
        pass
    
    # Add extra compilation flags
    cmd.extend(extra_flags)
    
    # Add source files
    cmd.extend(str(f) for f in source_files)
    
    print(f"\nBuilding {module_name}...")
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd)
    return result.returncode == 0


def build_all_extensions():
    """Build all Fortran extensions"""
    print("\n" + "="*70)
    print("Building Fortran extensions")
    print("="*70)
    
    project_root = Path(__file__).parent
    fsrc_dir = project_root / "gwm" / "fsrc"
    output_dir = project_root / "gwm"
    
    # Change to gwm directory for building
    os.chdir(str(output_dir))
    
    success = True
    
    # 1. Build baseline module
    print("\n" + "-"*70)
    print("1. Building _baseline module (Lagrange multipliers)")
    print("-"*70)
    baseline_sources = [fsrc_dir / "baseline" / "baseline_lagrange_multipliers.f"]
    if not build_fortran_extension("_baseline", baseline_sources):
        print("✗ Failed to build _baseline module")
        success = False
    else:
        print("✓ Successfully built _baseline module")
    
    # 2. Build equtils module
    print("\n" + "-"*70)
    print("2. Building _equtils module (signal processing utilities)")
    print("-"*70)
    equtils_sources = [
        fsrc_dir / "equtils" / "smooth.f90",
        fsrc_dir / "equtils" / "taper.f90",
        fsrc_dir / "equtils" / "butterworth.f90",
        fsrc_dir / "equtils" / "zpa_clipping.f90"
    ]
    # Separate flags to avoid invalid concatenation in some gfortran builds
    equtils_flags = ['--f90flags=-fbounds-check', '--f90flags=-g']
    if not build_fortran_extension("_equtils", equtils_sources, equtils_flags):
        print("✗ Failed to build _equtils module")
        success = False
    else:
        print("✓ Successfully built _equtils module")
    
    # 3. Build rs_time_openmp module
    print("\n" + "-"*70)
    print("3. Building _rs_time_openmp module (response spectrum matching - OpenMP)")
    print("-"*70)
    rs_sources = [fsrc_dir / "rs" / "exactmethod_time_openmp.f90"]
    rs_flags = ['--f90flags=-fopenmp', '-lgomp', '-lpthread']
    if not build_fortran_extension("_rs_time_openmp", rs_sources, rs_flags):
        print("✗ Failed to build _rs_time_openmp module")
        success = False
    else:
        print("✓ Successfully built _rs_time_openmp module")
    
    return success


def main():
    """Main build function"""
    print("\n" + "="*70)
    print("GWM (Greedy Wavelet Method) - Build Script")
    print("="*70)
    
    print("\nChecking prerequisites...")
    print("-"*70)
    
    # Check Fortran compiler
    if not check_fortran_compiler():
        print("\n✗ No Fortran compiler found!")
        print("\nTo fix this, install a Fortran compiler:")
        system = platform.system()
        if system == "Darwin":  # macOS
            print("  brew install gcc")
        elif system == "Linux":
            print("  Ubuntu/Debian: sudo apt-get install gfortran")
            print("  Fedora/RHEL: sudo dnf install gcc-gfortran")
        elif system == "Windows":
            print("  Download MinGW-w64 from https://www.mingw-w64.org/")
            print("  Or use pre-compiled binaries from the gwm/resources folder")
        sys.exit(1)
    
    # Check f2py
    if not check_f2py():
        print("\n✗ f2py not found! Installing numpy...")
        if not subprocess.run([sys.executable, "-m", "pip", "install", "numpy>=1.26.4"]).returncode == 0:
            print("✗ Failed to install numpy")
            sys.exit(1)
        if not check_f2py():
            print("✗ f2py still not available after numpy installation")
            sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("✗ Failed to install Python dependencies")
        sys.exit(1)
    
    # Build Fortran extensions
    if not build_all_extensions():
        print("\n✗ Some Fortran extensions failed to build")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("✓ Build completed successfully!")
    print("="*70)
    print("\nGWM has been built and is ready to use.")
    print("You can now import it with: import gwm")
    print("\nRun test scripts to verify installation:")
    print("  python tests/Benchmark_RspMatch09_example.py")
    print("  python tests/test_RG1.60.py")
    

if __name__ == "__main__":
    main()
