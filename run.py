import os
import sys

src_dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.append(src_dir)

from src.main_menu import main_menu

if __name__ == "__main__":
    main_menu()
