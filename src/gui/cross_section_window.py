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
        
        # プレースホルダーラベル
        label = ttk.Label(
            main_frame,
            text=f"断面表示 #{self.window_id}\n\n(機能は後で実装)",
            font=('TkDefaultFont', 14),
            justify=tk.CENTER
        )
        label.pack(fill=tk.BOTH, expand=True)
    
    @classmethod
    def get_instances(cls):
        """すべての開いているウィンドウのリストを取得"""
        return cls._instances.copy()
    
    @classmethod
    def close_all(cls):
        """すべての断面表示ウィンドウを閉じる"""
        for instance in cls._instances.copy():
            instance.destroy()
