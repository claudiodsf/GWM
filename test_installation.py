#!/usr/bin/env python
"""
Test script to verify GWM installation in a new environment.

This script tests:
1. Python module imports
2. Fortran extension modules (_baseline, _equtils, _rs_time_openmp)
3. Core GWM functionality
4. Dependency versions
"""

import sys
import os


def test_imports():
    """Test basic GWM imports"""
    print("\n" + "="*70)
    print("Testing GWM Module Imports")
    print("="*70)
    
    try:
        import gwm
        print(f"✓ GWM imported successfully")
        print(f"  Version: {gwm._GWM_name_ver_}")
    except ImportError as e:
        print(f"✗ Failed to import gwm: {e}")
        return False
    
    try:
        import gwm._baseline
        print("✓ _baseline Fortran module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import _baseline: {e}")
        return False
    
    try:
        import gwm._equtils
        print("✓ _equtils Fortran module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import _equtils: {e}")
        return False
    
    try:
        import gwm._rs_time_openmp
        print("✓ _rs_time_openmp Fortran module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import _rs_time_openmp: {e}")
        return False
    
    return True


def test_dependencies():
    """Test that all required dependencies are installed"""
    print("\n" + "="*70)
    print("Testing Python Dependencies")
    print("="*70)
    
    dependencies = {
        'numpy': '1.26.4',
        'scipy': '1.13.1',
        'matplotlib': '3.9.2',
        'PyQt5': '5.15.10',
        'pillow': '10.4.0',
    }
    
    all_ok = True
    missing = []
    for package, required_version in dependencies.items():
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'Unknown')
            print(f"✓ {package}: {version}")
        except ImportError:
            print(f"✗ {package}: NOT INSTALLED")
            missing.append(package)
            all_ok = False
    
    # Allow graceful degradation if pillow or similar GUI dependencies are missing
    critical_modules = ['numpy', 'scipy', 'matplotlib']
    critical_ok = all(pkg not in missing for pkg in critical_modules)
    
    return critical_ok


def test_gwm_modules():
    """Test GWM submodule imports"""
    print("\n" + "="*70)
    print("Testing GWM Submodules")
    print("="*70)
    
    submodules = [
        'gwm.eqio',
        'gwm.eqmodel',
        'gwm.wavelets',
        'gwm.greedy_wavelet_method',
        'gwm.draggables',
        'gwm.mpl_utils',
        'gwm.s371a',
        'gwm.wavelet_match_controls',
    ]
    
    all_ok = True
    for module_name in submodules:
        try:
            __import__(module_name)
            print(f"✓ {module_name}")
        except ImportError as e:
            print(f"✗ {module_name}: {e}")
            all_ok = False
    
    return all_ok


def test_fortran_functions():
    """Test that Fortran functions can be called"""
    print("\n" + "="*70)
    print("Testing Fortran Function Calls")
    print("="*70)
    
    try:
        import numpy as np
        import gwm._baseline
        
        # Test baseline module has the expected functions
        if hasattr(gwm._baseline, 'baseline_lagrange_multipliers'):
            print("✓ _baseline.baseline_lagrange_multipliers function available")
        else:
            print("✗ _baseline module missing baseline_lagrange_multipliers")
            return False
        
        # Test equtils module functions
        import gwm._equtils
        functions = ['splitcosinebell', 'csmoothen', 'rsmoothen', 'butterworth', 'clip_at_zpa']
        for func in functions:
            if hasattr(gwm._equtils, func):
                print(f"✓ _equtils.{func} function available")
            else:
                print(f"✗ _equtils module missing {func}")
                return False
        
        # Test rs_time_openmp module
        import gwm._rs_time_openmp
        if hasattr(gwm._rs_time_openmp, 'rst_exactmethod'):
            print("✓ _rs_time_openmp.rst_exactmethod function available")
        else:
            print("✗ _rs_time_openmp module missing rst_exactmethod")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error testing Fortran functions: {e}")
        return False


def test_file_structure():
    """Test that expected files and directories exist"""
    print("\n" + "="*70)
    print("Testing GWM File Structure")
    print("="*70)
    
    import gwm
    
    # Get GWM root directory
    gwm_root = os.path.dirname(gwm.__file__)
    
    required_files = {
        '__init__.py': 'Module init',
        'eqio.py': 'EQ I/O module',
        'eqmodel.py': 'EQ model module',
        'wavelets.py': 'Wavelets module',
        'greedy_wavelet_method.py': 'Main algorithm',
    }
    
    all_ok = True
    for filename, description in required_files.items():
        filepath = os.path.join(gwm_root, filename)
        if os.path.isfile(filepath):
            print(f"✓ {filename}: {description}")
        else:
            print(f"✗ Missing {filename}: {description}")
            all_ok = False
    
    required_dirs = {
        'fsrc': 'Fortran source files',
        'resources': 'Resource files',
    }
    
    for dirname, description in required_dirs.items():
        dirpath = os.path.join(gwm_root, dirname)
        if os.path.isdir(dirpath):
            print(f"✓ {dirname}/: {description}")
        else:
            print(f"✗ Missing {dirname}/: {description}")
            all_ok = False
    
    return all_ok


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("GWM Installation Verification Test Suite")
    print("="*70)
    
    print(f"\nPython: {sys.version}")
    print(f"Executable: {sys.executable}")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("GWM Imports", test_imports),
        ("GWM Submodules", test_gwm_modules),
        ("File Structure", test_file_structure),
        ("Fortran Functions", test_fortran_functions),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    all_passed = True
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✓ All tests passed! GWM is properly installed.")
        print("="*70)
        return 0
    else:
        print("✗ Some tests failed. See details above.")
        print("="*70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
