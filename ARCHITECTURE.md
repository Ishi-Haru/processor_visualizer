# Processor Visualizer

このフォルダ構成について参照してください。

## プロジェクト構成

```
processor_visualizer/
├── main.py                 # アプリケーションのエントリーポイント
├── example_data/           # サンプルデータフォルダ
├── src/
│   ├── __init__.py
│   ├── core/              # ビジネスロジック層
│   │   ├── __init__.py
│   │   └── processor_manager.py    # Processorデータ管理
│   │
│   ├── visualization/     # データ可視化層
│   │   ├── __init__.py
│   │   ├── config.py              # 可視化設定
│   │   └── plotter.py             # プロット処理
│   │
│   └── gui/              # ユーザーインターフェース層
│       ├── __init__.py
│       ├── main_window.py         # メインウィンドウ
│       └── widgets.py             # カスタムウィジェット
```

## 各モジュールの責任

### core/processor_manager.py
- **責任**: Processorの読み込みと管理
- **主要クラス**: `ProcessorManager`
- **責務**:
  - フォルダからProcessorを読み込む
  - チャンネル選択を管理
  - データの抽出

### visualization/config.py
- **責任**: 可視化設定の一元管理
- **内容**:
  - カラーマップ設定
  - グラフのサイズやDPI
  - ラベル定義

### visualization/plotter.py
- **責任**: データのプロット処理
- **主要クラス**: `DataPlotter`
- **責務**:
  - データの形状に応じたプロット
  - 複数のプロット方法の実装
  - Matplotlib Figureの生成

### gui/widgets.py
- **責任**: GUIウィジェットの実装
- **主要クラス**: 
  - `ControlFrame`: 操作パネル
  - `InfoFrame`: データ情報表示
- **責務**:
  - UI要素の配置と管理
  - ユーザー入力の処理

### gui/main_window.py
- **責任**: アプリケーションウィンドウの統合
- **主要クラス**: `MainWindow`
- **責務**:
  - GUI全体の統合
  - イベントハンドリング
  - 各層の連携

## 設計パターン

- **責任の分離**: 各モジュールが単一の責務を持つ
- **層の分離**:
  - core: ビジネスロジック（Processorとの連携）
  - visualization: データ表示ロジック
  - gui: ユーザーインターフェース
- **依存性の方向**: GUI層 → visualization層 → core層

## 実行方法

```bash
python main.py
```

## 拡張性

新しい機能を追加する際:
1. **新しいプロット方法**: `visualization/plotter.py`に追加
2. **新しいUI要素**: `gui/widgets.py`に追加
3. **新しいビジネスロジック**: `core/processor_manager.py`を拡張
4. **設定の変更**: `visualization/config.py`を編集
