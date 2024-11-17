import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk, ImageFont
import textwrap

# Globális változók
current_file_path = None
current_image = None
zoom_level = 1.0  # Alapértelmezett zoom szint

def open_tpf_file():
    file_path = filedialog.askopenfilename(filetypes=[("TPF files", "*.tpf")])
    
    if file_path:
        global current_file_path, current_image, zoom_level
        current_file_path = file_path
        image_data, width, height = read_tpf_image(file_path)
        current_image = image_data  # Beállítjuk a globális current_image változót
        zoom_level = 1.0  # Reseteljük a zoom szintet
        show_image(image_data, width, height, zoom_level)

def read_tpf_image(file_path):
    with open(file_path, 'r') as file:
        size_line = file.readline().strip()
        width, height = map(int, size_line.split('x'))
        image = Image.new("RGB", (width, height), color="white")  # Fehér háttér
        for line in file:
            line = line.strip()
            if line:
                coord_part, color_part = line.split(' ')
                x, y = map(int, coord_part.strip('()').split(','))
                r, g, b = map(int, color_part.strip('()').split(','))
                image.putpixel((x, y), (r, g, b))
    
    return image, width, height

def show_image(image_data, width, height, zoom_level=1.0):
    global current_image
    current_image = image_data
    image = scale_image(image_data, zoom_level)
    
    image_tk = ImageTk.PhotoImage(image)
    image_label.config(image=image_tk)
    image_label.image = image_tk
    image_label.pack(fill="both", expand=True)
    text_frame.pack_forget()

    # Az aktuális zoom szint kiírása
    zoom_label.config(text=f"Current Zoom: {zoom_level:.2f}")
    
    # Zoom gombok megjelenítése
    show_zoom_buttons()

def scale_image(image_data, zoom_level):
    # A kép nagyítása a zoom szintjével
    new_size = (int(image_data.width * zoom_level), int(image_data.height * zoom_level))
    return image_data.resize(new_size, Image.Resampling.LANCZOS)

def zoom_in():
    global zoom_level
    zoom_level = min(zoom_level + 0.1, 3.0)  # Maximum 3.0 nagyítás
    if current_image:  # Csak akkor jelenítse meg, ha van betöltött kép
        show_image(current_image, current_image.width, current_image.height, zoom_level)

def zoom_out():
    global zoom_level
    zoom_level = max(zoom_level - 0.1, 0.5)  # Minimum 0.5 nagyítás
    if current_image:  # Csak akkor jelenítse meg, ha van betöltött kép
        show_image(current_image, current_image.width, current_image.height, zoom_level)

def hide_zoom_buttons():
    zoom_in_button.pack_forget()
    zoom_out_button.pack_forget()
    zoom_label.pack_forget()

def show_zoom_buttons():
    # Csak akkor jelenítjük meg a zoom gombokat, ha van betöltött kép
    if current_image:
        zoom_in_button.pack(side=tk.LEFT, padx=10)
        zoom_out_button.pack(side=tk.LEFT, padx=10)
        zoom_label.pack()
# Function to create a sample image

def create_sample_image():
    global current_image, zoom_level
    width, height = 300, 200
    sample_image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sample_image)
    
    # Add text to the sample image
    text = "If you can read this,\nyou successfully made an image"
    text_position = (10, height // 2 - 20)  # Center the text vertically
    draw.text(text_position, text, fill="black")
    
    current_image = sample_image
    zoom_level = 1.0
    show_image(current_image, 300, 200)

def show_text_view():
    if current_file_path:
        with open(current_file_path, 'r') as file:
            content = file.read()
            text_box.delete(1.0, tk.END)
            text_box.insert(tk.END, content)
        
        text_frame.pack(fill="both", expand=True)
        image_label.pack_forget()
        hide_zoom_buttons()  # Szöveges nézetben rejtjük el a zoom gombokat

def save_text_view():
    if current_file_path:
        with open(current_file_path, 'w') as file:
            content = text_box.get(1.0, tk.END)
            file.write(content)
        messagebox.showinfo("Mentés", "Változások elmentve!")

def create_default_image():
    """Alapértelmezett üzenettel rendelkező kép létrehozása, sortörésekkel."""
    width, height = 300, 200
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)

    # Alapértelmezett font beállítása (a rendszer alapértelmezett fontját használjuk, vagy a PIL-es fontot)
    try:
        font = ImageFont.truetype("arial.ttf", 16)  # Ha elérhető a font, próbálkozhatunk vele
    except IOError:
        font = ImageFont.load_default()  # Ha nem elérhető, alapértelmezett fontot használunk

    text = "To import an image, please click File -> Open TPF File."
    # Használjuk a textwrap modult, hogy a szöveg beleférjen a képre
    wrapped_text = textwrap.fill(text, width=20)  # 20 karakteres sorokra tördeljük

    # A tördelés után középre helyezzük a szöveget
    lines = wrapped_text.split("\n")
    total_height = sum([draw.textbbox((0, 0), line, font=font)[3] for line in lines])  # Szöveg magasságának kiszámítása
    y_position = (height - total_height) // 2  # A szöveg középre igazítása

    # Tördelés utáni sorok rajzolása
    for line in lines:
        text_width, text_height = draw.textbbox((0, 0), line, font=font)[2:4]
        x_position = (width - text_width) // 2  # A szöveg középre igazítása
        draw.text((x_position, y_position), line, font=font, fill="black")
        y_position += text_height  # Y pozíció frissítése a következő sorhoz

    return image

# Tkinter ablak létrehozása
root = tk.Tk()
root.title("TPF Image Viewer")

# Menü létrehozása
menu_bar = tk.Menu(root)

# File menü
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open TPF File", command=open_tpf_file)
file_menu.add_command(label="Save", command=save_text_view)
file_menu.add_command(label="Create Sample Image", command=create_sample_image)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

# View menü
view_menu = tk.Menu(menu_bar, tearoff=0)
view_menu.add_command(label="Image View", command=lambda: open_tpf_file() if current_file_path is None else show_image(*read_tpf_image(current_file_path), zoom_level))
view_menu.add_command(label="Text View", command=show_text_view)
menu_bar.add_cascade(label="View", menu=view_menu)

# Menü hozzáadása az ablakhoz
root.config(menu=menu_bar)

# Kép megjelenítésére szolgáló címke
image_label = tk.Label(root)

# Szöveges nézethez szükséges keret és görgetősáv
text_frame = tk.Frame(root)
scrollbar = tk.Scrollbar(text_frame)
text_box = tk.Text(text_frame, yscrollcommand=scrollbar.set)

scrollbar.config(command=text_box.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_box.pack(side=tk.LEFT, fill="both", expand=True)

# Zoom szint kijelzése
zoom_label = tk.Label(root, text=f"Current Zoom: {zoom_level:.2f}")

# Zoom gombok
zoom_in_button = tk.Button(root, text="+", command=zoom_in)
zoom_out_button = tk.Button(root, text="-", command=zoom_out)

# Alapértelmezett kép betöltése
current_image = create_default_image()
show_image(current_image, current_image.width, current_image.height, zoom_level)

# Az ablak futtatása
root.mainloop()
