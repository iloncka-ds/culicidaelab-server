import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now run the Solara app
from culicidaelab_server.main import Page

if __name__ == "__main__":
    Page()
