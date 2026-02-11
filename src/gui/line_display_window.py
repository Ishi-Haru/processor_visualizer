"""Line display window module"""
import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from ..visualization.plotter import DataPlotter
from ..core.processor_manager import ProcessorManager

matplotlib.use('TkAgg')


class LineDisplayWindow(tk.Toplevel):
    """ライン表示ウィンドウ"""
    
    # クラス変数：ウィンドウのカウント
    _count = 0
    _instances = []
    
    def __init__(self, parent, processor_manager=None):
        super().__init__(parent)
        
        # ウィンドウ番号をインクリメント
        LineDisplayWindow._count += 1
        self.window_id = LineDisplayWindow._count
        
        # Processor情報を保存
        self.processor_manager = processor_manager
        
        # 現在の座標を保存
        self.current_x = 0
        self.current_y = 0
        self.canvas = None
        
        # ウィンドウ設定
        self.title(f"ライン表示 #{self.window_id}")
        self.geometry("800x600")
        
        # インスタンスリストに追加
        LineDisplayWindow._instances.append(self)
        
        # ウィンドウクローズ時の処理
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # UI を設定
        self.setup_ui()
    
    def _on_closing(self):
        """ウィンドウクローズ時の処理"""
        LineDisplayWindow._instances.remove(self)
        self.destroy()
    
    def setup_ui(self):
        """UIレイアウトをセットアップ"""
        # メインコンテナ
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # タイトルラベル
        title_label = ttk.Label(
            main_frame,
            text=f"ライン表示 #{self.window_id}",
            font=('TkDefaultFont', 14),
            justify=tk.CENTER
        )
        title_label.pack(fill=tk.X, pady=10)
        
        # チャンネル選択フレーム
        channel_frame = ttk.LabelFrame(main_frame, text="チャンネル選択", padding=10)
        channel_frame.pack(fill=tk.X, pady=10)
        
        # 横軸チャンネル
        ttk.Label(channel_frame, text="横軸:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.x_channel_var = tk.StringVar()
        self.x_channel_combo = ttk.Combobox(channel_frame, textvariable=self.x_channel_var, 
                                            state="readonly", width=50)
        self.x_channel_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.x_channel_combo.bind('<<ComboboxSelected>>', self.on_channel_selected)
        
        # 縦軸チャンネル
        ttk.Label(channel_frame, text="縦軸:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.y_channel_var = tk.StringVar()
        self.y_channel_combo = ttk.Combobox(channel_frame, textvariable=self.y_channel_var, 
                                            state="readonly", width=50)
        self.y_channel_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.y_channel_combo.bind('<<ComboboxSelected>>', self.on_channel_selected)
        
        channel_frame.grid_columnconfigure(1, weight=1)
        
        # 座標情報を表示するフレーム
        coord_frame = ttk.LabelFrame(main_frame, text="現在の座標", padding=10)
        coord_frame.pack(fill=tk.X, pady=10)
        
        # X座標ラベル
        ttk.Label(coord_frame, text="X座標:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.x_coord_label = ttk.Label(coord_frame, text="未設定", font=('TkDefaultFont', 12, 'bold'))
        self.x_coord_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Y座標ラベル
        ttk.Label(coord_frame, text="Y座標:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.y_coord_label = ttk.Label(coord_frame, text="未設定", font=('TkDefaultFont', 12, 'bold'))
        self.y_coord_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # プロット表示フレーム
        self.plot_frame = ttk.Frame(main_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # チャンネルリストを取得して設定
        if self.processor_manager is not None:
            self._populate_channels()
        else:
            placeholder_label = ttk.Label(
                self.plot_frame,
                text="チャンネルを選択してください",
                font=('TkDefaultFont', 12),
                justify=tk.CENTER,
                foreground="gray"
            )
            placeholder_label.pack(fill=tk.BOTH, expand=True)
    
    @classmethod
    def get_instances(cls):
        """すべての開いているウィンドウのリストを取得"""
        return cls._instances.copy()
    
    @classmethod
    def close_all(cls):
        """すべてのライン表示ウィンドウを閉じる"""
        for instance in cls._instances.copy():
            instance.destroy()
    
    def update_coordinates(self, x: int, y: int):
        """座標情報を更新"""
        self.current_x = int(x)
        self.current_y = int(y)
        self.x_coord_label.config(text=str(self.current_x))
        self.y_coord_label.config(text=str(self.current_y))
        
        # チャンネルが両方選択されていればプロットを更新
        if self.x_channel_combo.current() >= 0 and self.y_channel_combo.current() >= 0:
            self.update_plot()
    
    def _populate_channels(self):
        """チャンネルリストを取得して表示"""
        if self.processor_manager is None:
            return
        
        all_labels = self.processor_manager.processor.get_label_list()
        values = [f"{i}: {label}" for i, label in enumerate(all_labels)]
        self.x_channel_combo['values'] = values
        self.y_channel_combo['values'] = values
    
    def on_channel_selected(self, event=None):
        """チャンネル選択時のコールバック"""
        if self.x_channel_combo.current() >= 0 and self.y_channel_combo.current() >= 0:
            self.update_plot()
    
    def update_plot(self):
        """プロットを更新"""
        if self.processor_manager is None or self.processor_manager.processor is None:
            return
        
        x_ch_idx = self.x_channel_combo.current()
        y_ch_idx = self.y_channel_combo.current()
        
        if x_ch_idx < 0 or y_ch_idx < 0:
            return
        
        try:
            # メインウィンドウのcurrent_managerを変更せず、一時的に取得
            x_manager = self.processor_manager.processor.get_manager(index=x_ch_idx)
            x_full_data = x_manager.extract()
            
            y_manager = self.processor_manager.processor.get_manager(index=y_ch_idx)
            y_full_data = y_manager.extract()
            
            # (x, y)座標でのz方向データを抽出
            y_size_x, x_size_x, z_size_x = x_full_data.shape
            y_size_y, x_size_y, z_size_y = y_full_data.shape
            
            # 座標を範囲内に制限
            x_coord = max(0, min(int(self.current_x), x_size_x - 1, x_size_y - 1))
            y_coord = max(0, min(int(self.current_y), y_size_x - 1, y_size_y - 1))
            
            # (x, y)座標でのz方向データを取得
            x_data = x_full_data[y_coord, x_coord, :]  # shape: (z_size_x,)
            y_data = y_full_data[y_coord, x_coord, :]  # shape: (z_size_y,)
            
            # データ長が一致しない場合は短い方に合わせる
            min_len = min(len(x_data), len(y_data))
            x_data = x_data[:min_len]
            y_data = y_data[:min_len]
            
            # ラベルを取得
            all_labels = self.processor_manager.processor.get_label_list()
            x_label = all_labels[x_ch_idx]
            y_label = all_labels[y_ch_idx]
            
            # プロット
            figure = DataPlotter.plot_xy_line(x_data, y_data, x_label, y_label, x_coord, y_coord)
            self.display_figure(figure)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def display_figure(self, figure):
        """プロットを表示"""
        # 前のキャンバスを削除
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        self.canvas = FigureCanvasTkAgg(figure, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
