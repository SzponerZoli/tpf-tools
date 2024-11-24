import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageTk

# Globális változók
current_file_path = None
current_image = None
drawing = False  # Rajzolás indítása
last_x, last_y = 0, 0  # Az utolsó egér pozíciója
current_color = "#000000"  # Kezdő szín
tool = "pen"  # Kezdő eszköz: toll
eraser_size = 10  # Radír mérete
pen_size = 2  # Toll vastagsága

# Rajzoló objektum létrehozása
draw = None

def open_tpf_file():
    """Betölt egy TPF fájlt és megjeleníti azt a vásznon."""
    file_path = filedialog.askopenfilename(filetypes=[("TPF files", "*.tpf")])
    if file_path:
        global current_file_path, current_image, draw
        current_file_path = file_path
        image_data, width, height = read_tpf_image(file_path)
        current_image = image_data
        draw = ImageDraw.Draw(current_image)  # Rajzoló objektum inicializálása
        show_image(image_data, width, height)

def save_tpf_file():
    """A rajz mentése TPF formátumban (mentés meglévő fájlba)."""
    if current_file_path:  # Ha van már mentett fájl
        with open(current_file_path, 'w') as file:
            width, height = current_image.size
            file.write(f"{width}x{height}\n")
            for y in range(height):
                for x in range(width):
                    r, g, b = current_image.getpixel((x, y))
                    if (r, g, b) != (255, 255, 255):  # Csak a színes pixeleket írjuk ki
                        file.write(f"({x},{y}) ({r},{g},{b})\n")
    else:
        save_as_tpf_file()  # Ha nincs mentett fájl, akkor "Save As"-t hívunk

def save_as_tpf_file():
    """A rajz mentése TPF formátumban új fájlként."""
    file_path = filedialog.asksaveasfilename(defaultextension=".tpf", filetypes=[("TPF files", "*.tpf")])
    if file_path:
        global current_file_path
        current_file_path = file_path
        save_tpf_file()  # A mentést itt végezzük el

def read_tpf_image(file_path):
    """Betölti a TPF fájlt és visszaadja a képet."""
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

def show_image(image_data, width, height):
    """Kép megjelenítése a Tkinter ablakban."""
    image_tk = ImageTk.PhotoImage(image_data)
    canvas.create_image(0, 0, image=image_tk, anchor="nw")
    canvas.image = image_tk

def start_drawing(event):
    """A rajzolás kezdete."""
    global drawing, last_x, last_y
    drawing = True
    last_x, last_y = event.x, event.y

def stop_drawing(event):
    """A rajzolás befejezése."""
    global drawing
    drawing = False

def draw_line(event):
    """A rajzolás működése, ha az egér mozgásban van."""
    global last_x, last_y
    if drawing:
        if tool == "pen":
            # Rajzolás a canvasra
            canvas.create_line(last_x, last_y, event.x, event.y, width=pen_size, fill=current_color, capstyle="round", smooth=True)
            # Kép frissítése a putpixel helyett a rajzoló objektummal
            draw.line([last_x, last_y, event.x, event.y], fill=current_color, width=pen_size)
        elif tool == "eraser":
            canvas.create_oval(event.x - eraser_size, event.y - eraser_size, event.x + eraser_size, event.y + eraser_size,
                               fill="white", outline="white")  # Radír: fehérre törli
            erase_on_image(event.x, event.y)  # Radírozás frissítése a képen
        last_x, last_y = event.x, event.y

def clear_canvas():
    """Törli a vásznat (üresre állítja a képet)."""
    global current_image, draw
    width, height = current_image.size
    current_image = Image.new("RGB", (width, height), color="white")  # Üres kép
    draw = ImageDraw.Draw(current_image)  # Újra inicializáljuk a rajzoló objektumot
    canvas.delete("all")  # Töröljük a rajzot
    show_image(current_image, width, height)  # Újrarajzoljuk a tiszta képet

def select_color():
    """Színválasztó a rajzoláshoz."""
    global current_color
    color = colorchooser.askcolor()[1]  # Szín választása
    if color:
        current_color = color

def select_tool(new_tool):
    """Kiválasztja az eszközt (pen, eraser)."""
    global tool
    tool = new_tool

def erase_on_image(x, y):
    """A radír alkalmazása az aktuális képen."""
    global current_image
    width, height = current_image.size
    for i in range(-eraser_size, eraser_size):
        for j in range(-eraser_size, eraser_size):
            if 0 <= x + i < width and 0 <= y + j < height:
                current_image.putpixel((x + i, y + j), (255, 255, 255))  # Radír: fehér háttér
    show_image(current_image, width, height)

def set_pen_size(size):
    """Beállítja a toll vastagságát."""
    global pen_size
    pen_size = size

def set_eraser_size(size):
    """Beállítja a radír méretét."""
    global eraser_size
    eraser_size = size

# Tkinter ablak létrehozása
root = tk.Tk()
root.title("TPF Paint")

# Vászon létrehozása
canvas = tk.Canvas(root, width=600, height=400, bg="white")
canvas.pack()

canvas.bind("<Button-1>", start_drawing)  # Bal egérgomb: rajzolás
canvas.bind("<B1-Motion>", draw_line)  # Mozgás közbeni rajzolás
canvas.bind("<ButtonRelease-1>", stop_drawing)  # Egér felengedése: megállás

# Menü létrehozása
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open TPF File", command=open_tpf_file)
file_menu.add_command(label="Save TPF File", command=save_tpf_file)
file_menu.add_command(label="Save As", command=save_as_tpf_file)
file_menu.add_command(label="Clear", command=clear_canvas)
menu_bar.add_cascade(label="File", menu=file_menu)

tool_menu = tk.Menu(menu_bar, tearoff=0)
tool_menu.add_command(label="Pen", command=lambda: select_tool("pen"))
tool_menu.add_command(label="Eraser", command=lambda: select_tool("eraser"))
menu_bar.add_cascade(label="Tools", menu=tool_menu)

size_menu = tk.Menu(menu_bar, tearoff=0)
size_menu.add_command(label="Pen Size 1", command=lambda: set_pen_size(1))
size_menu.add_command(label="Pen Size 2", command=lambda: set_pen_size(2))
size_menu.add_command(label="Pen Size 5", command=lambda: set_pen_size(5))
size_menu.add_command(label="Eraser Size 5", command=lambda: set_eraser_size(5))
size_menu.add_command(label="Eraser Size 10", command=lambda: set_eraser_size(10))
menu_bar.add_cascade(label="Sizes", menu=size_menu)

color_menu = tk.Menu(menu_bar, tearoff=0)
color_menu.add_command(label="Select Color", command=select_color)
menu_bar.add_cascade(label="Colors", menu=color_menu)

root.config(menu=menu_bar)

# Kezdő kép betöltése
current_image = Image.new("RGB", (600, 400), color="white")
draw = ImageDraw.Draw(current_image)
show_image(current_image, 600, 400)

# Az ablak futtatása
root.mainloop()
