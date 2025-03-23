from PyQt6.QtWidgets import (QMainWindow, QApplication, QPushButton, QFileDialog,
                           QVBoxLayout, QWidget, QLabel, QMessageBox)
from PyQt6.QtGui import QImage, QPixmap
from PIL import Image
import sys
import os

class ImageConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TPF Image Converter")
        self.setGeometry(100, 100, 400, 200)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create buttons
        self.btn_to_tpf = QPushButton("Convert JPG/PNG to TPF", self)
        self.btn_from_tpf = QPushButton("Convert TPF to JPG/PNG", self)
        
        # Add status label
        self.status_label = QLabel("Ready", self)
        
        # Add widgets to layout
        layout.addWidget(self.btn_to_tpf)
        layout.addWidget(self.btn_from_tpf)
        layout.addWidget(self.status_label)
        
        # Connect buttons to functions
        self.btn_to_tpf.clicked.connect(self.convert_to_tpf)
        self.btn_from_tpf.clicked.connect(self.convert_from_tpf)

    def convert_to_tpf(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Select Image",
                "",
                "Image Files (*.jpg *.png *.jpeg)"
            )
            
            if not file_path:
                return
                
            # Open and verify image
            img = Image.open(file_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            width, height = img.size
            pixels = img.load()
            
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save TPF",
                os.path.splitext(file_path)[0] + ".tpf",
                "TPF Files (*.tpf)"
            )
            
            if not save_path:
                return
                
            with open(save_path, 'w') as f:
                # Write header
                f.write(f"1 {width}x{height}\n")
                
                # Write pixel data
                for y in range(height):
                    for x in range(width):
                        r, g, b = pixels[x, y]
                        f.write(f"({x},{y}) ({r},{g},{b})\n")
            
            self.status_label.setText("Conversion successful!")
            QMessageBox.information(self, "Success", "Image converted to TPF successfully!")
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error converting image: {str(e)}")

    def convert_from_tpf(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select TPF",
                "",
                "TPF Files (*.tpf)"
            )
            
            if not file_path:
                return
                
            with open(file_path, 'r') as f:
                lines = f.readlines()
                
            if not lines:
                raise ValueError("Empty TPF file")
                
            # Parse header
            header = lines[0].strip().split()
            if len(header) != 2:
                raise ValueError("Invalid TPF header format")
                
            version, dimensions = header
            if version != "1":
                raise ValueError(f"Unsupported TPF version: {version}")
                
            try:
                width, height = map(int, dimensions.split('x'))
            except:
                raise ValueError("Invalid dimensions in TPF header")
            
            # Create new image
            img = Image.new('RGB', (width, height), color='black')
            pixels = img.load()
            
            # Parse pixels
            for line in lines[1:]:
                try:
                    coords, colors = line.strip().split(') (')
                    x, y = map(int, coords[1:].split(','))
                    r, g, b = map(int, colors.split(','))
                    
                    if not (0 <= x < width and 0 <= y < height):
                        continue
                    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                        continue
                        
                    pixels[x, y] = (r, g, b)
                except:
                    continue
            
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Image",
                os.path.splitext(file_path)[0] + ".png",
                "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)"
            )
            
            if not save_path:
                return
                
            img.save(save_path)
            self.status_label.setText("Conversion successful!")
            QMessageBox.information(self, "Success", "TPF converted to image successfully!")
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error converting TPF: {str(e)}")

def main():
    app = QApplication(sys.argv)
    converter = ImageConverter()
    converter.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()