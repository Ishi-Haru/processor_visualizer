"""Processor データ管理を行うモジュール"""
from modules.processor import ZXYDataProcessor
from typing import Optional, List
import numpy as np


class ProcessorManager:
    """Processorの読み込みと管理を行うクラス"""
    
    def __init__(self):
        self.processor: Optional[ZXYDataProcessor] = None
        self.current_manager = None
        self.current_index = None
        self.channel_shapes: List[tuple] = []  # Store shapes for all channels
        self.selectable: List[bool] = []  # Track which channels are selectable (z_size == 1)
    
    def load_from_folder(self, folder_path: str) -> List[str]:
        """
        フォルダからProcessorを読み込み、すべてのチャンネルを返す
        
        Args:
            folder_path: Processorフォルダのパス
            
        Returns:
            チャンネルラベルリスト (すべてのチャンネル)
        """
        self.processor = ZXYDataProcessor.load_from_folder(folder_path=folder_path)
        all_labels = self.processor.get_label_list()
        
        # Store all channels with their shapes and selectability
        self.channel_shapes = []
        self.selectable = []
        
        for i, label in enumerate(all_labels):
            manager = self.processor.get_manager(index=i)
            x_size, y_size, z_size = manager.get_data_shape()
            self.channel_shapes.append((x_size, y_size, z_size))
            self.selectable.append(z_size == 1)
        
        return all_labels
    
    def get_data_size(self) -> tuple:
        """
        processorのデータサイズを取得（全体のx, y, zサイズ）
        
        Returns:
            (x_size, y_size, z_size) のタプル
        """
        if self.processor is None:
            raise RuntimeError("Processor not loaded")
        
        return self.processor.get_data_size()
    
    def select_channel(self, index: int) -> tuple:
        """
        チャンネルを選択し、データ形状情報を取得
        
        Args:
            index: チャンネルインデックス
            
        Returns:
            (x_size, y_size, z_size) のタプル
        """
        if self.processor is None:
            raise RuntimeError("Processor not loaded")
        
        if index < 0 or index >= len(self.channel_shapes):
            raise IndexError(f"Channel index {index} out of range")
        
        self.current_manager = self.processor.get_manager(index=index)
        self.current_index = index
        
        return self.channel_shapes[index]
    
    def extract_data(self) -> np.ndarray:
        """
        現在のチャンネルのデータを抽出
        
        Returns:
            3D ndarray
        """
        if self.current_manager is None:
            raise RuntimeError("No channel selected")
        
        return self.current_manager.extract()
    
    def get_current_label(self) -> str:
        """現在のチャンネルラベルを取得"""
        if self.processor is None or self.current_index is None:
            return "N/A"
        
        all_labels = self.processor.get_label_list()
        return all_labels[self.current_index]
    
    def get_channel_shapes(self) -> List[tuple]:
        """すべてのチャンネルの形状情報を取得"""
        return self.channel_shapes
    
    def is_selectable(self, index: int) -> bool:
        """チャンネルが選択可能かどうかを取得"""
        if 0 <= index < len(self.selectable):
            return self.selectable[index]
        return False
