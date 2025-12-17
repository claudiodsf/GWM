# GWM Installation Guide

This document provides step-by-step instructions for installing the Greedy Wavelet Method (GWM) across different operating systems.

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher (3.10+ recommended)
- **Fortran Compiler**: Required to compile Fortran extensions
- **C Compiler**: Required as dependency of Fortran compiler
- **Virtual Environment**: Highly recommended (venv or conda)

### Fortran Compiler Installation

#### macOS (using Homebrew)

```bash
brew install gcc
```

This installs the full GNU toolchain including gfortran.

#### Ubuntu/Debian Linux

```bash
sudo apt-get update
sudo apt-get install gfortran build-essential python3-dev
```

#### Fedora/RHEL/CentOS

```bash
sudo dnf install gcc gcc-c++ gcc-gfortran make python3-devel
```

#### Windows

**Option 1: MinGW-w64 (Recommended)**
1. Download from https://www.mingw-w64.org/
2. Run the installer and select:
   - Architecture: x86_64
   - Threads: posix
   - Exception handling: dwarf2 (or seh)
3. Add MinGW bin directory to PATH
4. Verify installation:
   ```cmd
   gfortran --version
   ```

**Option 2: Use Pre-built Binaries**
Pre-compiled .pyd files for Python 3.12 are included in `gwm/` folder. If you use Python 3.12, you may skip Fortran compilation.

## Installation Methods

### Method 1: Automatic Installation (Recommended)

This method automatically installs all dependencies and compiles Fortran code.

#### Step 1: Create a Virtual Environment

```bash
# Create environment
python -m venv gwm_env

# Activate environment
# On macOS/Linux:
source gwm_env/bin/activate
# On Windows:
gwm_env\Scripts\activate
```

#### Step 2: Run the Build Script

```bash
cd /path/to/GWM
python build_gwm.py
```

This script will:
- Check for Fortran compiler availability
- Install all Python dependencies (numpy, scipy, matplotlib, PyQt5, pillow)
- Compile Fortran extensions (_baseline, _equtils, _rs_time_openmp)
- Report the status of each step

#### Step 3: Verify Installation

```bash
python -c "import gwm; print(gwm._GWM_name_ver_)"
```

You should see: `GWM (Greedy Wavelet Method): 2024.3.12.RIC2024`

### Method 2: Manual Installation with setup.py

For more control over the installation process:

```bash
# Create virtual environment
python -m venv gwm_env
source gwm_env/bin/activate  # or gwm_env\Scripts\activate on Windows

# Install with setuptools
cd /path/to/GWM
pip install -e .

# Or build and install separately:
python setup.py build_ext --inplace
pip install -r requirements.txt
```

### Method 3: Using pip with editable install

```bash
cd /path/to/GWM
pip install -e .
```

This installs GWM in development mode, allowing you to edit the code.

### Method 4: Conda Installation

If you use Anaconda/Miniconda:

```bash
# Create environment with dependencies
conda create -n gwm python=3.12 gfortran numpy scipy matplotlib PyQt5 pillow

# Activate environment
conda activate gwm

# Install GWM
cd /path/to/GWM
python build_gwm.py
```

## Troubleshooting

### Error: "Fortran compiler not found"

**Solution**: Install a Fortran compiler as described in the Prerequisites section.

On macOS, if you installed gcc but still get this error:
```bash
# Verify gfortran is available
which gfortran

# If not found, ensure it's in PATH
export PATH="/usr/local/bin:$PATH"
```

### Error: "f2py not found" or "numpy not found"

**Solution**: Install numpy before building:

```bash
pip install "numpy>=1.26.4"
```

### Error: "can't find a MSVC compiler" (Windows)

**Solution**: You need either:
1. MinGW-w64 installed and in PATH
2. Or Visual Studio C++ build tools

For MinGW, ensure it's properly installed and in your system PATH.

### ImportError: "cannot import name '_baseline'"

**Possible causes:**
- Fortran compilation failed (check build output)
- Wrong Python version (pre-built .pyd files only for Python 3.12)
- Missing compiled .pyd files

**Solution:**
1. Verify compiler is installed: `gfortran --version`
2. Try manual rebuild: `python build_gwm.py --force`
3. Check that compiled files exist: `ls gwm/*.so` (Linux/Mac) or `dir gwm\*.pyd` (Windows)

### TypeError: "required argument is not a numpy array"

**Cause**: Numpy version mismatch

**Solution**: Update numpy:
```bash
pip install --upgrade "numpy~=1.26.4"
```

## Using Pre-built Binaries

The `gwm/` folder contains pre-compiled Python extension modules (.pyd files) for Python 3.12 on Windows:

- `_baseline.cp312-win_amd64.pyd`
- `_equtils.cp312-win_amd64.pyd`
- `_rs_time_openmp.cp312-win_amd64.pyd`

If you're using Python 3.12 on Windows, these files will be used automatically. The `mingw64_deps/` folder contains required DLL files for these pre-built modules.

## Running Tests

After successful installation, verify everything works:

```bash
# Navigate to tests directory
cd tests

# Run benchmark test
python Benchmark_RspMatch09_example.py

# Run another test
python test_RG1.60.py
```

Both tests should run without errors and generate output.

## Using GWM in Your Code

### Basic Usage

```python
import gwm
print(gwm._GWM_name_ver_)

# Import specific modules
from gwm.greedy_wavelet_method import WaveletMatch
from gwm.eqio import load_at2_file

# Your code here
```

### Interactive GUI

The GWM GUI can be launched through the wavelet_match_controls module:

```python
# Check wavelet_match_controls.py for entry point details
```

## Uninstalling GWM

```bash
# If installed with pip
pip uninstall gwm

# Or if installed in development mode
cd /path/to/GWM
pip uninstall -e .

# Then remove the source directory
rm -rf /path/to/GWM
```

## Getting Help

For issues, questions, or to report bugs:

1. Check the [super_brief_manual.md](docs/super_brief_manual.md)
2. Review test scripts in `tests/` folder for usage examples
3. Examine the Python docstrings in the source code
4. Check the original publication for algorithm details

## Citation

If you use GWM in your research, please cite:

> Nie, G., Graizer, V., & Seber, G. (2023). A greedy algorithm for wavelet-based time domain response spectrum matching. *Nuclear Engineering and Design*, 410, 112384. https://doi.org/10.1016/j.nucengdes.2023.112384

## License

See [LICENSE.md](LICENSE.md) for licensing information.
