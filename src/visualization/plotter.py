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

