"""
AFM Processor Visualizer - Main entry point
"""
import sys
import tkinter as tk
from pathlib import Path

# src フォルダをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.gui.main_window import MainWindow


def main():
    """アプリケーション起動"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()