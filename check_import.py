import sys
import os

print("Python path:")
for p in sys.path:
    print(f"- {p}")

print("\nCurrent directory:", os.getcwd())
print("\nContents of src directory:", os.listdir("src"))

try:
    import redoc

    print("\nSuccessfully imported redoc!")
    print(f"redoc module: {redoc}")
    print(f"redoc.__file__: {redoc.__file__}")
except ImportError as e:
    print(f"\nFailed to import redoc: {e}")
    print("\nTrying to add src to path...")
    import sys

    sys.path.insert(0, os.path.abspath("."))
    sys.path.insert(0, os.path.abspath("src"))
    try:
        import redoc

        print("Successfully imported redoc after adding src to path!")
        print(f"redoc module: {redoc}")
        print(f"redoc.__file__: {redoc.__file__}")
    except ImportError as e2:
        print(f"Still failed to import redoc: {e2}")
