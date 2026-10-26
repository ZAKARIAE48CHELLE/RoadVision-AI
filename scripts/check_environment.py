"""
RoadVision AI - Environment Diagnostic and Hardware Benchmark Script
This script inspects Python version, PyTorch installation, CUDA/GPU capability,
RAM, disk space, and core package dependencies.
"""

import sys
import os
import platform
import shutil
import psutil

def check_python():
    print("=" * 60)
    print("1. Python Environment")
    print("=" * 60)
    print(f"Python Version    : {platform.python_version()}")
    print(f"Python Executable : {sys.executable}")
    print(f"Operating System  : {platform.system()} {platform.release()} ({platform.machine()})")

def check_hardware():
    print("\n" + "=" * 60)
    print("2. Hardware & Resource Assessment")
    print("=" * 60)
    
    # RAM
    ram = psutil.virtual_memory()
    total_ram_gb = ram.total / (1024 ** 3)
    available_ram_gb = ram.available / (1024 ** 3)
    print(f"Total System RAM   : {total_ram_gb:.2f} GB")
    print(f"Available RAM      : {available_ram_gb:.2f} GB")

    # Storage
    cwd = os.getcwd()
    total_d, used_d, free_d = shutil.disk_usage(cwd)
    print(f"Current Drive Disk Space (free) : {free_d / (1024 ** 3):.2f} GB / {total_d / (1024 ** 3):.2f} GB")

def check_torch_and_gpu():
    print("\n" + "=" * 60)
    print("3. Deep Learning & GPU Acceleration")
    print("=" * 60)
    try:
        import torch
        print(f"PyTorch Version   : {torch.__version__}")
        cuda_avail = torch.cuda.is_available()
        print(f"CUDA Available    : {cuda_avail}")
        if cuda_avail:
            device_count = torch.cuda.device_count()
            print(f"GPU Device Count  : {device_count}")
            for i in range(device_count):
                props = torch.cuda.get_device_properties(i)
                vram_gb = props.total_memory / (1024 ** 3)
                print(f"  - GPU {i}: {props.name} | VRAM: {vram_gb:.2f} GB | Compute: {props.major}.{props.minor}")
        else:
            print("  [INFO] No CUDA-enabled GPU detected in PyTorch runtime.")
            print("  Training can run locally on CPU for test runs, or on Google Colab/Kaggle GPU for full-scale experiments.")
    except ImportError:
        print("[ERROR] PyTorch is not installed.")

def check_core_libraries():
    print("\n" + "=" * 60)
    print("4. Core Library Availability")
    print("=" * 60)
    packages = [
        ("cv2", "OpenCV"),
        ("ultralytics", "Ultralytics YOLO / RT-DETR"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("matplotlib", "Matplotlib"),
        ("seaborn", "Seaborn"),
        ("PIL", "Pillow"),
        ("yaml", "PyYAML"),
        ("streamlit", "Streamlit"),
    ]

    for mod_name, label in packages:
        try:
            mod = __import__(mod_name)
            ver = getattr(mod, "__version__", "installed")
            print(f"  [OK] {label:<25} : v{ver}")
        except ImportError:
            print(f"  [MISSING] {label:<25} : not installed")

if __name__ == "__main__":
    check_python()
    check_hardware()
    check_torch_and_gpu()
    check_core_libraries()
    print("\n" + "=" * 60)
    print("Diagnostic completed successfully.")
    print("=" * 60)
