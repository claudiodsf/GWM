#!/usr/bin/env python
"""
Setup script for GWM (Greedy Wavelet Method)

This script handles cross-platform compilation of Fortran extensions using f2py
and installation of all dependencies.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext


class F2pyBuildExt(build_ext):
    """Custom build_ext command to compile Fortran code using f2py"""
    
    def build_extension(self, ext):
        """Override build_extension to use f2py for Fortran compilation"""
        # We handle compilation manually via f2py commands
        pass
    
    def run(self):
        """Run custom f2py compilation"""
        # Check if Fortran compiler is available
        if not self._check_fortran_compiler():
            raise RuntimeError(
                "Fortran compiler not found. Please install:\n"
                "  - Linux/Mac: gfortran (part of gcc/brew)\n"
                "  - Windows: MinGW-w64 or Intel Fortran\n"
                "Installation hints:\n"
                "  - Ubuntu/Debian: sudo apt-get install gfortran\n"
                "  - Mac: brew install gcc\n"
                "  - Windows: Install MinGW-w64 or use pre-built binaries"
            )
        
        print("\n" + "="*70)
        print("Building Fortran extensions with f2py")
        print("="*70 + "\n")
        
        # Build each Fortran extension
        fsrc_dir = Path(__file__).parent / "gwm" / "fsrc"
        
        # 1. Build baseline module
        self._build_baseline(fsrc_dir)
        
        # 2. Build equtils module
        self._build_equtils(fsrc_dir)
        
        # 3. Build rs_time_openmp module
        self._build_rs_time_openmp(fsrc_dir)
        
        print("\n" + "="*70)
        print("Fortran compilation completed successfully")
        print("="*70 + "\n")
    
    def _check_fortran_compiler(self):
        """Check if a Fortran compiler is available"""
        compilers = ['gfortran', 'f77', 'f90']
        for compiler in compilers:
            try:
                subprocess.run(
                    [compiler, '--version'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
                print(f"Found Fortran compiler: {compiler}")
                return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return False
    
    def _run_f2py(self, module_name, source_files, extra_flags=None):
        """Run f2py to compile Fortran files into the package dir (in-place)."""
        # Compile directly into the source package directory so editable installs
        # can import the built extension modules.
        pkg_dir = Path(__file__).parent / "gwm"
        pkg_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable, "-m", "numpy.f2py",
            "-c",
            "-m", module_name,
        ]
        
        # Add compiler flags
        system = platform.system()
        if system == "Windows":
            cmd.extend(["--compiler=mingw32", "--fcompiler=gnu95"])
        else:
            cmd.extend(["--fcompiler=gnu95"])
        
        # Add extra flags if provided
        if extra_flags:
            for flag in extra_flags:
                cmd.append(flag)
        
        # Add source files
        cmd.extend(str(f) for f in source_files)
        
        print(f"\nCompiling {module_name}...")
        print(f"Command: {' '.join(cmd)}\n")
        # Run in the package dir so the resulting .so is placed under gwm/
        result = subprocess.run(cmd, cwd=str(pkg_dir))
        if result.returncode != 0:
            raise RuntimeError(f"f2py compilation failed for {module_name}")
    
    def _build_baseline(self, fsrc_dir):
        """Build the baseline (Lagrange multipliers) module"""
        source_files = [fsrc_dir / "baseline" / "baseline_lagrange_multipliers.f"]
        self._run_f2py("_baseline", source_files)
    
    def _build_equtils(self, fsrc_dir):
        """Build the equtils module"""
        source_files = [
            fsrc_dir / "equtils" / "smooth.f90",
            fsrc_dir / "equtils" / "taper.f90",
            fsrc_dir / "equtils" / "butterworth.f90",
            fsrc_dir / "equtils" / "zpa_clipping.f90"
        ]
        # Separate f90 flags to avoid shell-quoted concatenation issues
        extra_flags = ['--f90flags=-fbounds-check', '--f90flags=-g']
        self._run_f2py("_equtils", source_files, extra_flags)
    
    def _build_rs_time_openmp(self, fsrc_dir):
        """Build the rs_time_openmp module with OpenMP support"""
        source_files = [fsrc_dir / "rs" / "exactmethod_time_openmp.f90"]
        
        # Add OpenMP flags based on platform
        extra_flags = ['--f90flags=-fopenmp']
        
        # Add link flags for different platforms
        if platform.system() != "Windows":
            extra_flags.extend(["-lgomp", "-lpthread"])
        else:
            extra_flags.extend(["-lgomp", "-lpthread"])
        
        self._run_f2py("_rs_time_openmp", source_files, extra_flags)


def get_long_description():
    """Read long description from README"""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return "Greedy Wavelet Method (GWM) - Response spectrum matching algorithm"


setup(
    name="gwm",
    version="2024.3.12",
    author="Greedy Wavelet Method Contributors",
    description="Greedy Wavelet Method - Time domain response spectrum matching",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/gwm",
    packages=find_packages(),
    package_data={
        "gwm": [
            "resources/*",
            "fsrc/**/*",
        ]
    },
    include_package_data=True,
    install_requires=[
        "numpy~=1.26.4",
        "scipy~=1.13.1",
        "matplotlib~=3.9.2",
        "PyQt5~=5.15.10",
        "pillow~=10.4.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Fortran",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    ext_modules=[
        # Dummy extension objects to trigger build_ext
        Extension("gwm._baseline", sources=[]),
        Extension("gwm._equtils", sources=[]),
        Extension("gwm._rs_time_openmp", sources=[]),
    ],
    cmdclass={"build_ext": F2pyBuildExt},
    zip_safe=False,
)
