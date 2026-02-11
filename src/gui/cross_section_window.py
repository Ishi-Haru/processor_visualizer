"""Cross section display window module"""
import tkinter as tk
from tkinter import ttk


class CrossSectionWindow(tk.Toplevel):
    """断面表示ウィンドウ"""
    
    # クラス変数：ウィンドウのカウント
    _count = 0
    _instances = []
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # ウィンドウ番号をインクリメント
        CrossSectionWindow._count += 1
        self.window_id = CrossSectionWindow._count
        
        # ウィンドウ設定
        self.title(f"断面表示 #{self.window_id}")
        self.geometry("800x600")
        
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
        
        # プレースホルダーラベル
        placeholder_label = ttk.Label(
            main_frame,
            text="(機能は後で実装)",
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
        """すべての断面表示ウィンドウを閉じる"""
        for instance in cls._instances.copy():
            instance.destroy()
    
    def update_coordinates(self, x: int, y: int):
        """座標情報を更新"""
        self.x_coord_label.config(text=str(int(x)))
        self.y_coord_label.config(text=str(int(y)))
