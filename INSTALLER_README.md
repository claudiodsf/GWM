# GWM Installation & Build Guide

## Overview

This document describes the cross-platform installation and build system for the Greedy Wavelet Method (GWM) software. The new installer provides automatic Fortran compilation and dependency management, replacing the Windows-only batch scripts.

## What's New

### Previous Setup (Windows Only)
- Required manual Fortran compilation using batch files
- .pyd files only available for Python 3.12 on Windows
- Separate DLL dependency management
- Complex setup for other platforms

### New Setup (Cross-Platform)
- ✅ Automatic Fortran compilation with f2py
- ✅ Works on macOS, Linux, and Windows
- ✅ Supports Python 3.8+
- ✅ Single command installation
- ✅ Comprehensive error checking and reporting
- ✅ Automated test suite

## Files Added/Modified

### New Installer Files

1. **`setup.py`** - Standard Python setuptools configuration
   - Custom `build_ext` command for Fortran compilation
   - f2py-based extension building
   - Handles platform-specific compilation flags

2. **`pyproject.toml`** - Modern Python project configuration
   - PEP 517/518 compliant build backend
   - Dependency specifications
   - Development dependencies

3. **`build_gwm.py`** - Standalone build script
   - Does NOT require setuptools/pip
   - Can be run directly: `python build_gwm.py`
   - Useful for CI/CD pipelines
   - Comprehensive prerequisite checking

4. **`INSTALL.md`** - Detailed installation guide
   - Platform-specific instructions
   - Troubleshooting section
   - Multiple installation methods

5. **`test_installation.py`** - Verification test suite
   - Tests all three Fortran modules
   - Verifies dependency installation
   - Checks file structure
   - Validates Fortran function availability

## Quick Start

### Option 0: Conda env (environment.yml)

```bash
cd /path/to/GWM
conda env create -f environment.yml   # creates env "gwm"
conda activate gwm
pip install -e .
python test_installation.py
```

If you want MKL on Intel/AMD, edit `environment.yml` to use `mkl` instead of `libopenblas`/`blas=*=openblas` before creating the env.

### Option 1: Automatic Build (Recommended)

```bash
# Create virtual environment
python -m venv gwm_env
source gwm_env/bin/activate  # or gwm_env\Scripts\activate on Windows

# Run build script
cd /path/to/GWM
python build_gwm.py

# Verify installation
python test_installation.py
```

### Option 2: Using setup.py

```bash
python -m venv gwm_env
source gwm_env/bin/activate

cd /path/to/GWM
pip install -e .

# Test
python test_installation.py
```

### Option 3: Using pip directly

```bash
pip install -e /path/to/GWM
```

## Architecture

### Fortran Modules

Three Fortran extension modules are automatically compiled:

1. **`_baseline`** (baseline_lagrange_multipliers.f)
   - Lagrange multiplier calculations
   - Fixed-form Fortran 77

2. **`_equtils`** (smooth.f90, taper.f90, butterworth.f90, zpa_clipping.f90)
   - Signal processing utilities:
     - `splitcosinebell` - Split cosine window function
     - `csmoothen` / `rsmoothen` - Smoothing functions
     - `butterworth` - Butterworth filter implementation
     - `clip_at_zpa` - Zero-padding and clipping

3. **`_rs_time_openmp`** (exactmethod_time_openmp.f90)
   - Response spectrum matching using exact method
   - OpenMP parallelization support
   - Core algorithm implementation

### Compilation Process

```
Python 3.11+ with numpy
       ↓
    f2py wrapper
       ↓
   Fortran compiler (gfortran)
       ↓
    .so files (macOS/Linux) or .pyd files (Windows)
       ↓
   Dynamically loaded by Python
```

## Platform-Specific Notes

### macOS

Requirements:
```bash
brew install gcc  # Installs gfortran
```

The build system automatically detects `gfortran` and compiles extensions as `.so` files.

### Linux (Ubuntu/Debian)

Requirements:
```bash
sudo apt-get install gfortran build-essential python3-dev
```

### Linux (Fedora/RHEL)

Requirements:
```bash
sudo dnf install gcc gcc-c++ gcc-gfortran make python3-devel
```

### Windows

**Option A: MinGW-w64** (Recommended)
- Download from https://www.mingw-w64.org/
- Ensure `gfortran` is in PATH
- Build system auto-detects and uses `--compiler=mingw32 --fcompiler=gnu95` flags

**Option B: Pre-built Binaries**
- `.pyd` files for Python 3.12 are included in the `gwm/` folder
- If using Python 3.12, Fortran compilation can be skipped

**Option C: Visual Studio + Intel Fortran**
- Replace `gfortran` with Intel Fortran compiler (ifort)
- Update build scripts as needed

## Installation Verification

The `test_installation.py` script verifies:

1. **Dependencies**: NumPy, SciPy, Matplotlib, PyQt5, Pillow
2. **GWM Module**: Main package imports correctly
3. **Fortran Modules**: All three .so/.pyd files load
4. **Submodules**: All Python modules import without errors
5. **File Structure**: Required files and directories exist
6. **Function Availability**: Fortran functions are callable

Run verification:
```bash
python test_installation.py
```

Expected output:
```
✓ All tests passed! GWM is properly installed.
```

## Troubleshooting

### "Fortran compiler not found"

Install a Fortran compiler:

**macOS:**
```bash
brew install gcc
```

**Ubuntu/Debian:**
```bash
sudo apt-get install gfortran
```

**Windows:**
- Option 1: Install MinGW-w64
- Option 2: Use pre-built .pyd files for Python 3.12
- Option 3: Use Visual Studio with Intel Fortran

### "numpy.f2py not found"

f2py is part of NumPy. Ensure it's installed:
```bash
pip install "numpy>=1.26.4"
```

### ImportError: "cannot import name '_baseline'"

The Fortran extension didn't compile. Check:
1. Compiler is installed: `gfortran --version`
2. NumPy is installed: `python -c "import numpy"`
3. Build output for errors: Run `python build_gwm.py` again

### "dylib was built for newer macOS version"

Linker warnings about macOS version mismatch are normal with recent gcc/gfortran on macOS. The compiled extensions still work correctly.

## Development Mode

To install GWM in development mode (editable install):

```bash
cd /path/to/GWM
pip install -e .
```

This allows you to edit Python files and see changes immediately. Fortran changes still require recompilation:

```bash
python build_gwm.py
```

## Using Pre-built Binaries (Python 3.12 on Windows)

The repository includes pre-compiled `.pyd` files for Python 3.12 on Windows x64:

- `gwm/_baseline.cp312-win_amd64.pyd`
- `gwm/_equtils.cp312-win_amd64.pyd`
- `gwm/_rs_time_openmp.cp312-win_amd64.pyd`

Dependencies:
- `mingw64_deps/*.dll` - Runtime libraries

If you use Python 3.12 on Windows, Fortran compilation is optional. Just install Python dependencies:

```bash
pip install -r requirements.txt
```

For other Python versions or platforms, Fortran compilation is required.

## Integration with CI/CD

The standalone `build_gwm.py` script is useful for CI/CD:

```yaml
# GitHub Actions example
- name: Install build dependencies
  run: |
    sudo apt-get install gfortran  # Linux
    pip install numpy

- name: Build GWM
  run: python build_gwm.py

- name: Test installation
  run: python test_installation.py
```

## For Package Maintainers

### Creating Distribution Packages

Using setuptools:
```bash
python setup.py sdist bdist_wheel
```

Using build:
```bash
pip install build
python -m build
```

### Pre-building Wheels

For faster installation without compilation:

1. Build on reference system: `python -m build --wheel`
2. This creates `.whl` file with pre-compiled extensions
3. Users can install with: `pip install gwm-*.whl`

## Uninstallation

```bash
# If installed with pip
pip uninstall gwm

# Remove source directory
rm -rf /path/to/GWM
```

## Related Files

- `README.md` - Project overview
- `requirements.txt` - Python dependency pinning
- `docs/super_brief_manual.md` - User manual
- `tests/` - Example scripts and test data
- `gwm/fsrc/` - Fortran source code
- `mingw64_deps/` - Pre-compiled Windows runtime libraries

## Support

For issues:
1. Check [INSTALL.md](INSTALL.md) troubleshooting section
2. Run `test_installation.py` for diagnostics
3. Review build output: `python build_gwm.py 2>&1 | tee build.log`
4. Check original paper and documentation in `docs/`

## References

Original publication:
> Nie, G., Graizer, V., & Seber, G. (2023). A greedy algorithm for wavelet-based time domain response spectrum matching. *Nuclear Engineering and Design*, 410, 112384. https://doi.org/10.1016/j.nucengdes.2023.112384

## Version History

### v2024.3.12.RIC2024
- ✅ Cross-platform installer (macOS, Linux, Windows)
- ✅ Automatic Fortran compilation
- ✅ Comprehensive test suite
- ✅ Detailed installation guide
- ✅ Multiple installation methods
