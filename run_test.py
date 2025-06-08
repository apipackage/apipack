"""Run test directly to debug import issues."""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

print("Python path:", sys.path)
print("\nContents of src:", os.listdir("src"))
print("Contents of src/apipack:", os.listdir("src/apipack"))

try:
    import apipack

    print("\nSuccessfully imported apipack!")
    print(f"apipack module: {apipack}")
    print(f"apipack.__file__: {apipack.__file__}")
except ImportError as e:
    print(f"\nFailed to import apipack: {e}")
    import traceback

    traceback.print_exc()
