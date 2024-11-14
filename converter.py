import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

def read_tpf_image(file_path):
    """Olvassa a TPF fájlt, és visszaad egy Image objektumot."""
    with open(file_path, 'r') as file:
        size_line = file.readline().strip()
        width, height = map(int, size_line.split('x'))
        
        image = Image.new("RGB", (width, height), color="white")
        
        for line in file:
            line = line.strip()
            if line:
                coord_part, color_part = line.split(' ')
                x, y = map(int, coord_part.strip('()').split(','))
                r, g, b = map(int, color_part.strip('()').split(','))
                image.putpixel((x, y), (r, g, b))
    
    return image

def write_tpf_image(image, file_path):
    """Ment egy Image objektumot TPF formátumba."""
    width, height = image.size
    with open(file_path, 'w') as file:
        file.write(f"{width}x{height}\n")
        
        for x in range(width):
            for y in range(height):
                r, g, b = image.getpixel((x, y))
                if (r, g, b) != (255, 255, 255):
                    file.write(f"({x},{y}) ({r},{g},{b})\n")

def convert_file():
    conversion_type = conversion_var.get()
    
    try:
        if conversion_type == "TPF to PNG" or conversion_type == "TPF to JPG":
            tpf_path = filedialog.askopenfilename(title="Open TPF File", filetypes=[("TPF files", "*.tpf")])
            if not tpf_path:
                return
            
            image = read_tpf_image(tpf_path)
            save_format = "PNG" if conversion_type == "TPF to PNG" else "JPEG"
            save_extension = ".png" if save_format == "PNG" else ".jpg"
            save_path = filedialog.asksaveasfilename(defaultextension=save_extension, filetypes=[(f"{save_format} files", f"*{save_extension}")])
            
            if save_path:
                image.save(save_path, save_format)
                messagebox.showinfo("Success", f"TPF successfully converted to {save_format}!")

        elif conversion_type == "PNG to TPF" or conversion_type == "JPG to TPF":
            img_types = [("Image files", "*.png *.jpg"), ("PNG files", "*.png"), ("JPG files", "*.jpg")]
            img_path = filedialog.askopenfilename(title="Open Image File", filetypes=img_types)
            if not img_path:
                return
            
            image = Image.open(img_path).convert("RGB")
            tpf_path = filedialog.asksaveasfilename(defaultextension=".tpf", filetypes=[("TPF files", "*.tpf")])
            
            if tpf_path:
                write_tpf_image(image, tpf_path)
                messagebox.showinfo("Success", "Image successfully converted to TPF!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to convert: {e}")

# Tkinter GUI setup
root = tk.Tk()
root.title("TPF Converter")

# Conversion options dropdown
conversion_var = tk.StringVar(value="TPF to PNG")
conversion_options = ["TPF to PNG", "TPF to JPG", "PNG to TPF", "JPG to TPF"]
conversion_dropdown = ttk.Combobox(root, textvariable=conversion_var, values=conversion_options, state="readonly")
conversion_dropdown.pack(pady=10)

# Convert button
convert_button = tk.Button(root, text="Convert", command=convert_file)
convert_button.pack(pady=20)

root.mainloop()
