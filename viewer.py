import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QFileDialog, 
                            QScrollArea, QWidget, QMenuBar, QToolBar)
from PyQt6.QtGui import QPixmap, QImage, QAction, QIcon
from PyQt6.QtCore import Qt
from PIL import Image, ImageDraw, ImageFont

class TPFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TPF Image Viewer")
        
        # Kép megjelenítő rész
        self.scroll_area = QScrollArea()
        self.image_label = QLabel()
        self.scroll_area.setWidget(self.image_label)
        self.setCentralWidget(self.scroll_area)
        
        self.image = None
        self.zoom_level = 1.0
        
        self.init_ui()
        self.resize(800, 600)

    def init_ui(self):
        self.create_menu()
        self.create_toolbar()
        self.display_empty_image()

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        open_action = QAction('Open File', self)
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        sample_action = QAction('Sample Image', self)
        sample_action.triggered.connect(self.load_sample_image)
        file_menu.addAction(sample_action)

        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Zoom in action
        zoom_in_action = QAction(QIcon.fromTheme('zoom-in'), 'Zoom In', self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)

        # Zoom out action
        zoom_out_action = QAction(QIcon.fromTheme('zoom-out'), 'Zoom Out', self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)

    def display_empty_image(self):
        self.image_label.setPixmap(QPixmap())

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open TPF File", "", "TPF files (*.tpf)")
        if file_path:
            self.image = self.load_tpf(file_path)
            self.display_image()

    def open_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.current_directory = dir_path
            self.load_gallery(dir_path)

    def load_gallery(self, directory):
        self.gallery_list.clear()
        for file in os.listdir(directory):
            if file.endswith('.tpf'):
                self.gallery_list.addItem(file)

    def on_gallery_item_clicked(self, item):
        if self.current_directory:
            file_path = os.path.join(self.current_directory, item.text())
            self.image = self.load_tpf(file_path)
            self.display_image()

    def load_sample_image(self):
        # Create canvas with larger dimensions
        width, height = 800, 400
        self.image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(self.image)
        text = "Sample Image"

        try:
            # Load font from local fonts directory
            font_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                'fonts', 
                'Roboto-Bold.ttf'
            )
            font_size = 72  # Large font size
            font = ImageFont.truetype(font_path, font_size)
            
            # Get text size for centering
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Draw text centered on the image
            text_x = (width - text_width) // 2
            text_y = (height - text_height) // 2
            draw.text((text_x, text_y), text, fill="black", font=font)
            
        except Exception as e:
            print(f"Font loading error: {e}")
            # Fallback to default font if TTF loading fails
            font = ImageFont.load_default()
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = (width - text_width) // 2
            text_y = (height - text_height) // 2
            draw.text((text_x, text_y), text, fill="black", font=font)
        
        self.display_image()

    def load_tpf(self, file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            dimensions = lines[0].strip().split('x')
            width, height = int(dimensions[0]), int(dimensions[1])
            image = Image.new('RGB', (width, height), (255, 255, 255))

            for line in lines[1:]:
                parts = line.strip().split(' ')
                coords = parts[0].strip('()').split(',')
                color = tuple(map(int, parts[1].strip('()').split(',')))
                
                if len(coords) == 3:  # Run-length encoded
                    x, y, count = map(int, coords)
                    for i in range(count):
                        image.putpixel((x + i, y), color)
                else:  # Single pixel
                    x, y = map(int, coords)
                    image.putpixel((x, y), color)

            return image

    def display_image(self):
        if self.image:
            # Calculate new dimensions while maintaining aspect ratio
            new_width = int(self.image.width * self.zoom_level)
            new_height = int(self.image.height * self.zoom_level)
            
            # Resize the image using NEAREST sampling to keep pixels sharp
            resized_image = self.image.resize(
                (new_width, new_height),
                Image.NEAREST
            )
            
            # Convert to QImage and maintain stride alignment
            width = resized_image.width
            height = resized_image.height
            bytes_per_line = 3 * width  # RGB format = 3 bytes per pixel
            
            qimage = QImage(
                resized_image.tobytes(), 
                width, 
                height, 
                bytes_per_line,
                QImage.Format.Format_RGB888
            )
            
            pixmap = QPixmap.fromImage(qimage)
            self.image_label.setPixmap(pixmap)
            self.image_label.adjustSize()

    def wheelEvent(self, event):
        # More controlled zoom with minimum and maximum limits
        zoom_factor = 1.2
        
        if event.angleDelta().y() > 0:  # Zoom in
            self.zoom_level = min(10.0, self.zoom_level * zoom_factor)
        else:  # Zoom out
            self.zoom_level = max(0.1, self.zoom_level / zoom_factor)
        
        self.display_image()

    def zoom_in(self):
        zoom_factor = 1.2
        self.zoom_level = min(10.0, self.zoom_level * zoom_factor)
        self.display_image()

    def zoom_out(self):
        zoom_factor = 1.2
        self.zoom_level = max(0.1, self.zoom_level / zoom_factor)
        self.display_image()

    def save_image(self):
        if not self.image:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save TPF File",
            "",
            "TPF files (*.tpf)"
        )
        
        if file_path:
            if not file_path.endswith('.tpf'):
                file_path += '.tpf'
                
            with open(file_path, 'w') as file:
                # Write dimensions
                file.write(f"{self.image.width}x{self.image.height}\n")
                
                # Run-length encoding for pixels
                current_color = None
                count = 0
                current_y = 0
                
                for y in range(self.image.height):
                    for x in range(self.image.width):
                        color = self.image.getpixel((x, y))
                        
                        if current_color is None:
                            current_color = color
                            count = 1
                            continue
                        
                        if color == current_color and x < self.image.width - 1:
                            count += 1
                        else:
                            # Write the run
                            if count > 1:
                                file.write(f"({x-count},{y},{count}) ({current_color[0]},{current_color[1]},{current_color[2]})\n")
                            else:
                                file.write(f"({x-1},{y}) ({current_color[0]},{current_color[1]},{current_color[2]})\n")
                            current_color = color
                            count = 1
                    
                    # Write the last run of each line
                    if count > 0:
                        file.write(f"({self.image.width-count},{y},{count}) ({current_color[0]},{current_color[1]},{current_color[2]})\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = TPFViewer()
    viewer.show()
    sys.exit(app.exec())