"""GUI widgets module"""
import tkinter as tk
from tkinter import ttk


class InfoFrame(ttk.LabelFrame):
    """データ情報表示フレーム"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Data Information", **kwargs)
        
        self.info_label = ttk.Label(self, text="No data loaded", wraplength=900, justify=tk.LEFT)
        self.info_label.pack(padx=5, pady=5)
    
    def update_info(self, text: str):
        """情報テキストを更新"""
        self.info_label.config(text=text)


class SelectableListbox(tk.Frame):
    """選択肢を色分けして表示できるリストボックス"""
    
    def __init__(self, parent, width=50, height=5, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Listbox with scrollbar
        self.listbox = tk.Listbox(self, width=width, height=height, font=('TkDefaultFont', 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        self.selectable = []
        self.last_valid_index = -1
        self.callback = None
        
        self.listbox.bind('<<ListboxSelect>>', self._on_select)
    
    def _on_select(self, event):
        """リスト選択時のコールバック"""
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.selectable) and not self.selectable[index]:
                # 禁止項目が選択された場合は、前の有効な選択に戻す
                self.listbox.selection_clear(0, tk.END)
                if self.last_valid_index >= 0:
                    self.listbox.selection_set(self.last_valid_index)
                return
            if self.selectable[index]:
                self.last_valid_index = index
            if self.callback:
                self.callback()
    
    def _update_color(self, index):
        """指定インデックスの色を更新"""
        if index < len(self.selectable):
            if self.selectable[index]:
                self.listbox.itemconfig(index, {'fg': 'black'})
            else:
                self.listbox.itemconfig(index, {'fg': 'gray'})
    
    def set_items(self, items, selectable_list):
        """すべての選択肢を設定"""
        self.listbox.delete(0, tk.END)
        self.selectable = selectable_list[:]
        for item in items:
            self.listbox.insert(tk.END, item)
        
        # 色を設定
        for i in range(len(items)):
            self._update_color(i)
        
        # 最初の選択可能項目を選択
        for i, s in enumerate(self.selectable):
            if s:
                self.listbox.selection_set(i)
                self.last_valid_index = i
                break
    
    def current(self):
        """現在選択されているインデックスを取得"""
        selection = self.listbox.curselection()
        return selection[0] if selection else -1
    
    def bind_change(self, callback):
        """選択変更時のコールバックを設定"""
        self.callback = callback


class ControlFrame(ttk.Frame):
    """操作パネルフレーム"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Load button
        self.load_button = ttk.Button(self, text="Load Processor")
        self.load_button.pack(side=tk.LEFT, padx=5)
        
        # Channel selection label
        ttk.Label(self, text="Channel:").pack(side=tk.LEFT, padx=5)
        
        # Use SelectableListbox instead of Combobox
        self.channel_listbox = SelectableListbox(self, width=60, height=6)
        self.channel_listbox.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        # Visualize button
        self.visualize_button = ttk.Button(self, text="Visualize")
        self.visualize_button.pack(side=tk.LEFT, padx=5)
        
        # Export CSV button
        self.export_csv_button = ttk.Button(self, text="CSV出力")
        self.export_csv_button.pack(side=tk.LEFT, padx=5)
        
        # Open cross section window button
        self.cross_section_button = ttk.Button(self, text="断面表示を開く")
        self.cross_section_button.pack(side=tk.LEFT, padx=5)
        
        # Open line display window button
        self.line_display_button = ttk.Button(self, text="ライン表示を開く")
        self.line_display_button.pack(side=tk.LEFT, padx=5)
    
    def get_channel_index(self) -> int:
        """選択されたチャンネルのインデックスを取得"""
        return self.channel_listbox.current()
    
    def set_channels(self, labels: list, shapes: list = None, selectable: list = None):
        """
        チャンネルリストを設定
        
        Args:
            labels: チャンネルラベルのリスト
            shapes: (x_size, y_size, z_size)のタプルリスト (オプション)
            selectable: 各チャンネルが選択可能かを示すboolリスト (オプション)
        """
        selectable_list = selectable if selectable else [True] * len(labels)
        
        if shapes is None or len(shapes) != len(labels):
            # Shapes not provided, use labels only
            items = [f"{i}: {label}" for i, label in enumerate(labels)]
        else:
            # Include dimension information
            items = []
            for i, (label, shape) in enumerate(zip(labels, shapes)):
                x_size, y_size, z_size = shape
                items.append(f"{i}: {label} (x={x_size}, y={y_size}, z={z_size})")
        
        self.channel_listbox.set_items(items, selectable_list)
    
    def bind_load(self, callback):
        """Load ボタンのコールバックを設定"""
        self.load_button.config(command=callback)
    
    def bind_visualize(self, callback):
        """Visualize ボタンのコールバックを設定"""
        self.visualize_button.config(command=callback)
    
    def bind_export_csv(self, callback):
        """CSV出力ボタンのコールバックを設定"""
        self.export_csv_button.config(command=callback)
    
    def bind_cross_section_open(self, callback):
        """断面表示を開くボタンのコールバックを設定"""
        self.cross_section_button.config(command=callback)
    
    def bind_line_display_open(self, callback):
        """ライン表示を開くボタンのコールバックを設定"""
        self.line_display_button.config(command=callback)
    
    def bind_channel_change(self, callback):
        """チャンネル選択変更のコールバックを設定"""
        self.channel_listbox.bind_change(callback)
