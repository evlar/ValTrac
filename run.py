import os
import sys

# Add the src directory to the system path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.append(src_dir)

# Import and run the main menu
from main_menu import main_menu  # Notice the change here
if __name__ == "__main__":
    main_menu()  # And here
