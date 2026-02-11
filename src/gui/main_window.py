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
from .line_display_window import LineDisplayWindow


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
        self.control_frame.bind_line_display_open(self.on_open_line_display)
        
        # Info frame
        self.info_frame = InfoFrame(self.root)
        self.info_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Canvas frame with grid layout for sliders
        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid weights
        self.canvas_frame.grid_rowconfigure(1, weight=1)
        self.canvas_frame.grid_columnconfigure(1, weight=1)
        
        # Y-axis controls (left side)
        y_left_frame = ttk.Frame(self.canvas_frame)
        y_left_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=(0, 5))
        
        ttk.Label(y_left_frame, text="Y:").pack(side=tk.TOP, pady=5)
        self.y_slider = ttk.Scale(y_left_frame, orient=tk.VERTICAL, from_=100, to=0, command=self.on_y_slider_change)
        self.y_slider.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        self.y_value_label = ttk.Label(y_left_frame, text="0")
        self.y_value_label.pack(side=tk.TOP, pady=5)
        
        # Y-axis text input
        self.y_input_var = tk.StringVar(value="0")
        y_input = ttk.Entry(y_left_frame, textvariable=self.y_input_var, width=6)
        y_input.pack(side=tk.TOP, pady=5)
        y_input.bind('<Return>', self.on_y_input_change)
        
        # Matplotlib canvas (center)
        self.mpl_canvas_frame = ttk.Frame(self.canvas_frame)
        self.mpl_canvas_frame.grid(row=1, column=1, sticky=tk.NSEW)
        
        # X-axis controls (bottom)
        x_bottom_frame = ttk.Frame(self.canvas_frame)
        x_bottom_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=(5, 0))
        
        ttk.Label(x_bottom_frame, text="X:").pack(side=tk.LEFT, padx=5)
        self.x_slider = ttk.Scale(x_bottom_frame, orient=tk.HORIZONTAL, from_=0, to=100, command=self.on_x_slider_change)
        self.x_slider.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.x_value_label = ttk.Label(x_bottom_frame, text="0", width=5)
        self.x_value_label.pack(side=tk.LEFT, padx=5)
        
        # X-axis text input
        ttk.Label(x_bottom_frame, text="入力:").pack(side=tk.LEFT, padx=(20, 5))
        self.x_input_var = tk.StringVar(value="0")
        x_input = ttk.Entry(x_bottom_frame, textvariable=self.x_input_var, width=6)
        x_input.pack(side=tk.LEFT, padx=5)
        x_input.bind('<Return>', self.on_x_input_change)
    
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
                # Set slider ranges
                self.x_slider.config(from_=0, to=max(1, x_size-1))
                self.y_slider.config(from_=max(1, y_size-1), to=0)
                
                # Reset sliders to 0
                self.x_slider.set(0)
                self.y_slider.set(max(1, y_size-1))
                self.x_value_label.config(text="0")
                self.y_value_label.config(text=str(max(1, y_size-1)))
                self.x_input_var.set("0")
                self.y_input_var.set(str(max(1, y_size-1)))
                
                # Create empty 3D array (x_size, y_size, 1) filled with False/0
                empty_data = np.zeros((x_size, y_size, 1), dtype=bool)
                figure = DataPlotter.plot_data(empty_data.astype(float))
                self.display_figure(figure)
                
                # Broadcast initial coordinates to open windows
                self._broadcast_coordinates()
                
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
                
                # Update slider ranges based on channel size
                self.x_slider.config(from_=0, to=max(1, x_size-1))
                self.y_slider.config(from_=max(1, y_size-1), to=0)
                
                # Reset sliders to 0
                self.x_slider.set(0)
                self.y_slider.set(max(1, y_size-1))
                self.x_value_label.config(text="0")
                self.y_value_label.config(text=str(max(1, y_size-1)))
                self.x_input_var.set("0")
                self.y_input_var.set(str(max(1, y_size-1)))
                
                # Broadcast coordinates to open windows
                self._broadcast_coordinates()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to select channel: {str(e)}")
    
    def on_visualize(self):
        """可視化コールバック"""
        try:
            # リストボックスで現在選択されているチャンネルを再選択
            selected_index = self.control_frame.get_channel_index()
            if selected_index < 0:
                messagebox.showwarning("Warning", "No channel selected")
                return
            
            # 明示的にチャンネルを選択し直す（サブウィンドウで上書きされている可能性があるため）
            self.processor_manager.select_channel(selected_index)
            
            # データを取得してプロット
            data = self.processor_manager.extract_data()
            figure = DataPlotter.plot_data(data)
            self.display_figure(figure)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize: {str(e)}")
    
    def on_open_cross_section(self):
        """断面表示ウィンドウを開くコールバック"""
        window = CrossSectionWindow(self.root, self.processor_manager)
        # 現在の座標を新しいウィンドウに送信
        self._broadcast_coordinates()
    
    def on_open_line_display(self):
        """ライン表示ウィンドウを開くコールバック"""
        window = LineDisplayWindow(self.root, self.processor_manager)
        # 現在の座標を新しいウィンドウに送信
        self._broadcast_coordinates()
    
    def display_figure(self, figure):
        """Matplotlib figureを表示"""
        # Clear previous canvas
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        self.canvas = FigureCanvasTkAgg(figure, master=self.mpl_canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _broadcast_coordinates(self):
        """現在の座標をすべての開いているサブウィンドウに送信"""
        x_val = float(self.x_slider.get())
        y_val = float(self.y_slider.get())
        
        for window in CrossSectionWindow.get_instances():
            window.update_coordinates(x_val, y_val)
        
        for window in LineDisplayWindow.get_instances():
            window.update_coordinates(x_val, y_val)
    
    def on_x_slider_change(self, value):
        """X軸スライダー変更時のコールバック"""
        x_val = float(value)
        self.x_value_label.config(text=f"{x_val:.0f}")
        self.x_input_var.set(f"{x_val:.0f}")
        self._broadcast_coordinates()
    
    def on_y_slider_change(self, value):
        """Y軸スライダー変更時のコールバック"""
        y_val = float(value)
        self.y_value_label.config(text=f"{y_val:.0f}")
        self.y_input_var.set(f"{y_val:.0f}")
        self._broadcast_coordinates()
    
    def on_x_input_change(self, event):
        """X軸テキスト入力変更時のコールバック"""
        try:
            x_val = float(self.x_input_var.get())
            # スライダーの範囲内に制限
            x_min = float(self.x_slider.cget('from'))
            x_max = float(self.x_slider.cget('to'))
            x_val = max(x_min, min(x_max, x_val))
            self.x_slider.set(x_val)
            self.x_value_label.config(text=f"{x_val:.0f}")
            self._broadcast_coordinates()
        except ValueError:
            pass  # 無効な数値は無視
    
    def on_y_input_change(self, event):
        """Y軸テキスト入力変更時のコールバック"""
        try:
            y_val = float(self.y_input_var.get())
            # スライダーの範囲内に制限
            y_min = float(self.y_slider.cget('to'))
            y_max = float(self.y_slider.cget('from'))
            y_val = max(y_min, min(y_max, y_val))
            self.y_slider.set(y_val)
            self.y_value_label.config(text=f"{y_val:.0f}")
            self._broadcast_coordinates()
        except ValueError:
            pass  # 無効な数値は無視
