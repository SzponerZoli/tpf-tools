import sys
from PyQt6.QtWidgets import QApplication

# Create QApplication first
app = QApplication(sys.argv)

# Now import the rest
import os
import qtawesome as qta
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QColorDialog, QSpinBox, 
                            QLabel, QFileDialog, QMenuBar, QMenu, QDialog,
                            QGridLayout, QLineEdit, QFontDialog)
from PyQt6.QtGui import QPainter, QColor, QImage, QPen, QIcon, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QPoint, QSize, QPointF

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.init_canvas()
        self.eraser_mode = False
        self.text_mode = False
        self.text_to_draw = ""
        self.text_font = QFont("Arial", 12)

    def init_canvas(self, width=600, height=400):
        self.image = QImage(width, height, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)
        self.drawing = False
        self.brush_size = 3
        self.brush_color = QColor(0, 0, 0)
        self.last_point = QPoint()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.text_mode:
                painter = QPainter(self.image)
                painter.setFont(self.text_font)
                painter.setPen(QPen(self.brush_color))
                painter.drawText(event.pos(), self.text_to_draw)
                self.update()
            else:
                self.drawing = True
                self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.drawing:
            painter = QPainter(self.image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # For smooth circles
            
            if self.eraser_mode:
                painter.setPen(QPen(Qt.GlobalColor.white, 1))
                painter.setBrush(QColor(Qt.GlobalColor.white))
            else:
                painter.setPen(QPen(self.brush_color, 1))
                painter.setBrush(self.brush_color)

            # Calculate intermediate points for smooth line
            current_point = event.pos()
            steps = max(abs(current_point.x() - self.last_point.x()),
                       abs(current_point.y() - self.last_point.y())) // 2
            if steps == 0:
                steps = 1

            for i in range(steps + 1):
                x = self.last_point.x() + ((current_point.x() - self.last_point.x()) * i) / steps
                y = self.last_point.y() + ((current_point.y() - self.last_point.y()) * i) / steps
                radius = self.brush_size / 2
                painter.drawEllipse(QPointF(x, y), radius, radius)

            self.last_point = current_point
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def save_tpf(self, filename):
        width = self.image.width()
        height = self.image.height()
        
        with open(filename, 'w') as f:
            f.write(f"{width}x{height}\n")
            for y in range(height):
                for x in range(width):
                    color = self.image.pixelColor(x, y)
                    f.write(f"({x},{y}) ({color.red()},{color.green()},{color.blue()})\n")

    def load_tpf(self, filename):
        with open(filename, 'r') as f:
            # Read dimensions from first line
            dimensions = f.readline().strip()
            width, height = map(int, dimensions.split('x'))
            
            # Create new image
            self.init_canvas(width, height)
            
            # Read pixel data
            for line in f:
                if not line.strip():
                    continue
                pos, color = line.strip().split(') (')
                x, y = map(int, pos[1:].split(','))
                r, g, b = map(int, color.split(')')[0].split(','))
                self.image.setPixelColor(x, y, QColor(r, g, b))
        
        self.update()

class CanvasSizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Canvas Size")
        layout = QGridLayout(self)

        # Width input
        layout.addWidget(QLabel("Width:"), 0, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 3000)
        self.width_spin.setValue(600)
        layout.addWidget(self.width_spin, 0, 1)

        # Height input
        layout.addWidget(QLabel("Height:"), 1, 0)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 3000)
        self.height_spin.setValue(400)
        layout.addWidget(self.height_spin, 1, 1)

        # OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, 2, 0, 1, 2)

class TextInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Text")
        layout = QGridLayout(self)

        # Text input
        self.text_input = QLineEdit()
        layout.addWidget(QLabel("Text:"), 0, 0)
        layout.addWidget(self.text_input, 0, 1)

        # Font button
        font_btn = QPushButton("Choose Font")
        font_btn.clicked.connect(self.choose_font)
        layout.addWidget(font_btn, 1, 0, 1, 2)

        # OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, 2, 0, 1, 2)

        self.font = QFont("Arial", 12)

    def choose_font(self):
        font, ok = QFontDialog.getFont(self.font, self)
        if ok:
            self.font = font

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TPF Paint")
        self.resize(800, 600)
        
        # Create menubar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New", self.new_canvas)
        file_menu.addAction("Open", self.open_file)
        file_menu.addAction("Save", self.save_file)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Canvas Size", self.change_canvas_size)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # Color button
        color_btn = QPushButton()
        color_btn.setIcon(QIcon(qta.icon('fa5s.palette').pixmap(32, 32)))  # Changed from fa5.palette
        color_btn.setToolTip("Choose Color")
        color_btn.clicked.connect(self.choose_color)
        toolbar.addWidget(color_btn)
        
        # Text tool button
        self.text_btn = QPushButton()
        self.text_btn.setIcon(QIcon(qta.icon('fa5s.font').pixmap(32, 32)))  # Changed from fa5.font
        self.text_btn.setToolTip("Text Tool")
        self.text_btn.setCheckable(True)
        self.text_btn.clicked.connect(self.toggle_text_tool)
        toolbar.addWidget(self.text_btn)
        
        # Eraser toggle button
        self.eraser_btn = QPushButton()
        self.eraser_btn.setIcon(QIcon(qta.icon('fa5s.eraser').pixmap(32, 32)))  # Changed from fa5.eraser
        self.eraser_btn.setToolTip("Eraser")
        self.eraser_btn.setCheckable(True)
        self.eraser_btn.clicked.connect(self.toggle_eraser)
        toolbar.addWidget(self.eraser_btn)
        
        # Brush size
        toolbar.addWidget(QLabel("Brush size:"))
        self.brush_size = QSpinBox()
        self.brush_size.setValue(10)
        self.brush_size.valueChanged.connect(self.change_brush_size)
        toolbar.addWidget(self.brush_size)
        
        button_style = """
            QPushButton {
                padding: 5px;
                min-width: 32px;
                min-height: 32px;
            }
        """
        color_btn.setStyleSheet(button_style)
        self.text_btn.setStyleSheet(button_style)
        self.eraser_btn.setStyleSheet(button_style)
        
        layout.addLayout(toolbar)
        
        # Canvas
        self.canvas = Canvas()
        layout.addWidget(self.canvas)

    def new_canvas(self):
        self.canvas.init_canvas()

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open TPF File",
            "",
            "TPF Files (*.tpf);;All Files (*.*)"
        )
        if filename:
            self.canvas.load_tpf(filename)

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save TPF File",
            "",
            "TPF Files (*.tpf);;All Files (*.*)"
        )
        if filename:
            if not filename.endswith('.tpf'):
                filename += '.tpf'
            self.canvas.save_tpf(filename)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.brush_color = color

    def change_brush_size(self, size):
        self.canvas.brush_size = size

    def change_canvas_size(self):
        dialog = CanvasSizeDialog(self)
        if dialog.exec():
            width = dialog.width_spin.value()
            height = dialog.height_spin.value()
            self.canvas.init_canvas(width, height)

    def toggle_eraser(self):
        self.canvas.eraser_mode = self.eraser_btn.isChecked()

    def toggle_text_tool(self):
        if self.text_btn.isChecked():
            self.eraser_btn.setChecked(False)
            self.canvas.eraser_mode = False
            dialog = TextInputDialog(self)
            if dialog.exec():
                self.canvas.text_to_draw = dialog.text_input.text()
                self.canvas.text_font = dialog.font
                self.canvas.text_mode = True
        else:
            self.canvas.text_mode = False

if __name__ == '__main__':
    window = MainWindow()
    window.show()
    sys.exit(app.exec())