import os
import mimetypes
import platform
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import tkinter as tk
from tkinter import filedialog, messagebox

# 🧠 Extract EXIF date
def get_exif_date(file_path):
    try:
        img = Image.open(file_path)
        exif_data = img._getexif()
        if not exif_data:
            return None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "DateTimeOriginal":
                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S").timestamp()
    except:
        pass
    return None

# 🔍 Get sorted media files
def get_media_files(folder_path, sort_method, order="Ascending"):
    media_files = []
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        if os.path.isfile(full_path):
            mime_type, _ = mimetypes.guess_type(full_path)
            if mime_type and (mime_type.startswith("image") or mime_type.startswith("video")):
                size = os.path.getsize(full_path)

                if sort_method == "Date":
                    if mime_type.startswith("image"):
                        date = get_exif_date(full_path) or (
                            os.path.getctime(full_path) if platform.system() == "Windows" else os.path.getmtime(full_path)
                        )
                    else:
                        date = os.path.getctime(full_path) if platform.system() == "Windows" else os.path.getmtime(full_path)
                    key = date
                elif sort_method == "Size":
                    key = size
                else:  # Name
                    key = filename.lower()

                media_files.append((filename, size, key))

    reverse = (order == "Descending") if sort_method == "Size" else False
    return sorted(media_files, key=lambda x: x[2], reverse=reverse)

# 🛠️ Rename logic
def rename_files(folder_path, sort_by, rename_pattern, sort_order):
    media_files = get_media_files(folder_path, sort_by, sort_order)
    count = 0
    for i, (original_name, _, _) in enumerate(media_files):
        ext = os.path.splitext(original_name)[1]
        new_name = f"{i+1}{ext}" if rename_pattern == "Numbers" else f"IMG_{i+1:03}{ext}"

        src = os.path.join(folder_path, original_name)
        dst = os.path.join(folder_path, new_name)

        try:
            os.rename(src, dst)
            count += 1
        except Exception as e:
            print(f"Error renaming {original_name} → {new_name}: {e}")
    return count

# 📁 Select folder
def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)

# 🚀 Run renaming
def run_renamer():
    folder = folder_path.get()
    sort_by = sort_option.get()
    rename_style = rename_option.get()
    order = sort_order.get()

    if not os.path.exists(folder):
        messagebox.showerror("Error", "Invalid folder path.")
        return

    try:
        count = rename_files(folder, sort_by, rename_style, order)
        messagebox.showinfo("Success", f"Renamed {count} files successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

# 👁 Show/hide order dropdown
def update_sort_order_visibility(*args):
    if sort_option.get() == "Size":
        order_label.pack(pady=2)
        order_menu.pack()
    else:
        order_label.pack_forget()
        order_menu.pack_forget()

# 🖥️ GUI setup
root = tk.Tk()
root.title("Media File Renamer")
root.geometry("450x350")

folder_path = tk.StringVar()
sort_option = tk.StringVar(value="Size")
rename_option = tk.StringVar(value="IMG_001")
sort_order = tk.StringVar(value="Ascending")

sort_option.trace("w", update_sort_order_visibility)

# 🧱 GUI layout
tk.Label(root, text="📁 Select Folder:").pack(pady=5)
tk.Entry(root, textvariable=folder_path, width=45).pack()
tk.Button(root, text="Browse", command=browse_folder).pack(pady=5)

tk.Label(root, text="🔽 Sort files by:").pack(pady=5)
tk.OptionMenu(root, sort_option, "Size", "Name", "Date").pack()

order_label = tk.Label(root, text="⬆ Sort Order:")
order_menu = tk.OptionMenu(root, sort_order, "Ascending", "Descending")

tk.Label(root, text="🆕 Rename pattern:").pack(pady=5)
tk.OptionMenu(root, rename_option, "IMG_001", "Numbers").pack()

tk.Button(root, text="🚀 Rename Files", command=run_renamer, bg="green", fg="white").pack(pady=20)

update_sort_order_visibility()  # Set initial state

root.mainloop()
