"""Cross section display window module"""
import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from ..visualization.plotter import DataPlotter
from ..core.processor_manager import ProcessorManager

matplotlib.use('TkAgg')


class CrossSectionWindow(tk.Toplevel):
    """断面表示ウィンドウ"""
    
    # クラス変数：ウィンドウのカウント
    _count = 0
    _instances = []
    
    def __init__(self, parent, processor_manager=None):
        super().__init__(parent)
        
        # ウィンドウ番号をインクリメント
        CrossSectionWindow._count += 1
        self.window_id = CrossSectionWindow._count
        
        # Processor情報を保存
        self.processor_manager = processor_manager
        self.current_x = 0
        self.current_y = 0
        self.canvas = None
        
        # ウィンドウ設定
        self.title(f"断面表示 #{self.window_id}")
        self.geometry("900x700")
        
        # インスタンスリストに追加
        CrossSectionWindow._instances.append(self)
        
        # ウィンドウクローズ時の処理
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # UI を設定
        self.setup_ui()
    
    def _on_closing(self):
        """ウィンドウクローズ時の処理"""
        CrossSectionWindow._instances.remove(self)
        self.destroy()
    
    def setup_ui(self):
        """UIレイアウトをセットアップ"""
        # メインコンテナ
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # タイトルラベル
        title_label = ttk.Label(
            main_frame,
            text=f"断面表示 #{self.window_id}",
            font=('TkDefaultFont', 14),
            justify=tk.CENTER
        )
        title_label.pack(fill=tk.X, pady=10)
        
        # チャンネル選択フレーム
        channel_frame = ttk.LabelFrame(main_frame, text="チャンネル選択", padding=10)
        channel_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(channel_frame, text="Channel:").pack(side=tk.LEFT, padx=5)
        self.channel_var = tk.StringVar()
        self.channel_combo = ttk.Combobox(channel_frame, textvariable=self.channel_var, state="readonly", width=50)
        self.channel_combo.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        self.channel_combo.bind('<<ComboboxSelected>>', self.on_channel_selected)
        
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
        
        # チャンネルが選択されていない場合はプレースホルダーを表示
        if self.processor_manager is None:
            placeholder_label = ttk.Label(
                self.plot_frame,
                text="チャンネルを選択してください",
                font=('TkDefaultFont', 12),
                justify=tk.CENTER,
                foreground="gray"
            )
            placeholder_label.pack(fill=tk.BOTH, expand=True)
        else:
            self._populate_channels()
    
    @classmethod
    def get_instances(cls):
        """すべての開いているウィンドウのリストを取得"""
        return cls._instances.copy()
    
    @classmethod
    def close_all(cls):
        """すべての断面表示ウィンドウを閉じる"""
        for instance in cls._instances.copy():
            instance.destroy()
    
    def update_coordinates(self, x: int, y: int):
        """座標情報を更新"""
        self.current_x = int(x)
        self.current_y = int(y)
        self.x_coord_label.config(text=str(self.current_x))
        self.y_coord_label.config(text=str(self.current_y))
        
        # チャンネルが選択されていれば断面を再描画
        if self.channel_combo.current() >= 0:
            self.update_cross_section()
    
    def _populate_channels(self):
        """チャンネルリストを取得して表示"""
        if self.processor_manager is None:
            return
        
        all_labels = self.processor_manager.processor.get_label_list()
        values = [f"{i}: {label}" for i, label in enumerate(all_labels)]
        self.channel_combo['values'] = values
    
    def on_channel_selected(self, event=None):
        """チャンネル選択時のコールバック"""
        if self.channel_combo.current() >= 0:
            self.update_cross_section()
    
    def update_cross_section(self):
        """断面を描画"""
        if self.processor_manager is None or self.channel_combo.current() < 0:
            return
        
        try:
            channel_index = self.channel_combo.current()
            # チャンネルを選択
            x_size, y_size, z_size = self.processor_manager.select_channel(channel_index)
            # データを取得
            data = self.processor_manager.extract_data()
            
            # Y座標を確認
            y_index = min(int(self.current_y), y_size - 1)
            
            # Z方向のサイズに応じてプロット方法を変える
            if z_size == 1:
                # Z方向が1の場合：折れ線プロット（X軸に対する値）
                figure = DataPlotter.plot_cross_section_lineplot(data, y_index)
            else:
                # Z方向が複数の場合：カラーマップ（X-Z平面）
                figure = DataPlotter.plot_cross_section_colormap(data, y_index)
            
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
