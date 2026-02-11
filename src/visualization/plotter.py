"""Data visualization module"""
import numpy as np
from matplotlib.figure import Figure
from . import config


class DataPlotter:
    """データプロットを行うクラス"""
    
    @staticmethod
    def plot_data(data: np.ndarray) -> Figure:
        """
        2Dデータ(z-size == 1)をカラーマップでプロット
        
        Args:
            data: 3D ndarray (z-size は必ず 1)
            
        Returns:
            matplotlib Figure オブジェクト
        """
        if not isinstance(data, np.ndarray):
            data = np.asarray(data)
        
        if data.ndim != 3:
            raise ValueError(f"Expected 3D data, got {data.ndim}D")
        
        x_size, y_size, z_size = data.shape
        
        if z_size != 1:
            raise ValueError(f"Expected z_size == 1, got z_size == {z_size}")
        
        figure = Figure(figsize=config.FIGURE_SIZE, dpi=config.DPI)
        ax = figure.add_subplot(111)
        
        # Extract 2D data (z=0)
        xy = data[:, :, 0]
        x_size, y_size = xy.shape
        
        im = ax.imshow(xy.T, aspect='equal', origin='lower', cmap=config.DEFAULT_COLORMAP,
                      extent=[0, x_size, 0, y_size])
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title(f'xy plane (shape {xy.shape})')
        figure.colorbar(im, ax=ax, label='value')
        
        return figure
    
    @staticmethod
    def plot_cross_section_colormap(data: np.ndarray, y_index: int) -> Figure:
        """
        3Dデータの特定のY座標での断面をカラーマップでプロット
        
        Args:
            data: 3D ndarray (x, y, z)
            y_index: Y軸のインデックス
            
        Returns:
            matplotlib Figure オブジェクト
        """
        if not isinstance(data, np.ndarray):
            data = np.asarray(data)
        
        if data.ndim != 3:
            raise ValueError(f"Expected 3D data, got {data.ndim}D")
        
        x_size, y_size, z_size = data.shape
        
        # Y軸を固定して X-Z 平面を抽出
        y_index = min(int(y_index), y_size - 1)
        xz_slice = data[:, y_index, :]
        
        figure = Figure(figsize=config.FIGURE_SIZE, dpi=config.DPI)
        ax = figure.add_subplot(111)
        
        im = ax.imshow(xz_slice.T, aspect='auto', origin='lower', 
                      cmap=config.DEFAULT_COLORMAP,
                      extent=[0, x_size, 0, z_size])
        ax.set_xlabel('x')
        ax.set_ylabel('z')
        ax.set_title(f'Cross-section at y={y_index} (shape {xz_slice.shape})')
        figure.colorbar(im, ax=ax, label='value')
        
        return figure
    
    @staticmethod
    def plot_cross_section_lineplot(data: np.ndarray, y_index: int) -> Figure:
        """
        3Dデータの特定のY座標での断面を折れ線プロットで表示
        z方向のサイズが1の場合に使用
        
        Args:
            data: 3D ndarray (x, y, z) where z_size == 1
            y_index: Y軸のインデックス
            
        Returns:
            matplotlib Figure オブジェクト
        """
        if not isinstance(data, np.ndarray):
            data = np.asarray(data)
        
        if data.ndim != 3:
            raise ValueError(f"Expected 3D data, got {data.ndim}D")
        
        x_size, y_size, z_size = data.shape
        
        if z_size != 1:
            raise ValueError(f"Expected z_size == 1, got z_size == {z_size}")
        
        # Y軸を固定してX軸での断面を抽出
        y_index = min(int(y_index), y_size - 1)
        x_values = data[:, y_index, 0]  # shape: (x_size,)
        
        figure = Figure(figsize=config.FIGURE_SIZE, dpi=config.DPI)
        ax = figure.add_subplot(111)
        
        x_axis = np.arange(x_size)
        ax.plot(x_axis, x_values, marker='o', linestyle='-', linewidth=2)
        ax.set_xlabel('x')
        ax.set_ylabel('value')
        ax.set_title(f'Cross-section at y={y_index}')
        ax.grid(True, alpha=0.3)
        
        return figure

