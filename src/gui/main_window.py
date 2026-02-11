"""Main GUI window module"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import numpy as np
from ..core.processor_manager import ProcessorManager
from ..visualization.plotter import DataPlotter
from .widgets import ControlFrame, InfoFrame
from .cross_section_window import CrossSectionWindow


matplotlib.use('TkAgg')


class MainWindow:
    """メインウィンドウクラス"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AFM Processor Visualizer")
        self.root.geometry("1000x700")
        
        self.processor_manager = ProcessorManager()
        self.canvas = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """UIレイアウトをセットアップ"""
        # Control frame
        self.control_frame = ControlFrame(self.root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Bind callbacks
        self.control_frame.bind_load(self.on_load_processor)
        self.control_frame.bind_channel_change(self.on_channel_selected)
        self.control_frame.bind_visualize(self.on_visualize)
        self.control_frame.bind_cross_section_open(self.on_open_cross_section)
        
        # Info frame
        self.info_frame = InfoFrame(self.root)
        self.info_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Canvas frame
        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def on_load_processor(self):
        """Processor読み込みコールバック"""
        folder = filedialog.askdirectory(title="Select processor folder")
        if folder:
            try:
                labels = self.processor_manager.load_from_folder(folder)
                shapes = self.processor_manager.get_channel_shapes()
                selectable = [self.processor_manager.is_selectable(i) for i in range(len(labels))]
                self.control_frame.set_channels(labels, shapes, selectable)
                self.on_channel_selected()
                
                # Load and display empty colormap immediately
                x_size, y_size, z_size = self.processor_manager.get_data_size()
                # Create empty 3D array (x_size, y_size, 1) filled with False/0
                empty_data = np.zeros((x_size, y_size, 1), dtype=bool)
                figure = DataPlotter.plot_data(empty_data.astype(float))
                self.display_figure(figure)
                
                messagebox.showinfo("Success", f"Loaded {len(labels)} channels")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load processor: {str(e)}")
    
    def on_channel_selected(self):
        """チャンネル選択コールバック"""
        index = self.control_frame.get_channel_index()
        if index >= 0:
            try:
                x_size, y_size, z_size = self.processor_manager.select_channel(index)
                label = self.processor_manager.get_current_label()
                
                info_text = f"Channel: {label}\n"
                info_text += f"Data shape: x={x_size}, y={y_size}, z={z_size}"
                
                self.info_frame.update_info(info_text)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to select channel: {str(e)}")
    
    def on_visualize(self):
        """可視化コールバック"""
        try:
            data = self.processor_manager.extract_data()
            figure = DataPlotter.plot_data(data)
            self.display_figure(figure)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize: {str(e)}")
    
    def on_open_cross_section(self):
        """断面表示ウィンドウを開くコールバック"""
        CrossSectionWindow(self.root)
    
    def display_figure(self, figure):
        """Matplotlib figureを表示"""
        # Clear previous canvas
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        self.canvas = FigureCanvasTkAgg(figure, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
