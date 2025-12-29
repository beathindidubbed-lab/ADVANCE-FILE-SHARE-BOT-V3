"""Test if plugins folder exists"""
import os
import sys

print("=" * 50)
print("DEBUGGING PLUGINS FOLDER")
print("=" * 50)

print(f"\nCurrent directory: {os.getcwd()}")
print(f"\nPython path: {sys.path}")

print(f"\nDoes 'plugins' exist? {os.path.exists('plugins')}")
print(f"Is 'plugins' a directory? {os.path.isdir('plugins')}")

if os.path.exists('plugins'):
    print(f"\nContents of plugins/:")
    for item in os.listdir('plugins'):
        print(f"  - {item}")
else:
    print("\n❌ PLUGINS FOLDER NOT FOUND!")
    print("Listing current directory:")
    for item in os.listdir('.'):
        print(f"  - {item}")

print("\n" + "=" * 50)
