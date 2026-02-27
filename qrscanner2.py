import cv2
from pyzbar.pyzbar import decode
from tkinter import Text, END, filedialog
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import os

# ---------------- QR OKUMA ---------------- #

def read_qr(file_path):
    output_box.delete(1.0, END)

    if not os.path.exists(file_path):
        output_box.insert(END, "❌ Dosya yolu geçersiz!\n")
        return

    img = cv2.imread(file_path)

    if img is None:
        output_box.insert(END, "❌ Görsel yüklenemedi!\n")
        return

    # Büyük resmi küçült (RAM optimizasyonu)
    max_width = 800
    if img.shape[1] > max_width:
        scale = max_width / img.shape[1]
        img = cv2.resize(img, None, fx=scale, fy=scale)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    decoded_objects = decode(gray)

    filename = os.path.basename(file_path)
    output_box.insert(END, f"📂 Dosya: {filename}\n\n")

    if not decoded_objects:
        output_box.insert(END, "❌ QR kod bulunamadı.\n")
    else:
        for obj in decoded_objects:
            qr_data = obj.data.decode("utf-8")
            output_box.insert(END, f"✅ QR İçeriği:\n{qr_data}\n")

            # QR etrafına dikdörtgen çiz
            points = obj.polygon
            pts = [(p.x, p.y) for p in points]
            for i in range(len(pts)):
                cv2.line(img, pts[i], pts[(i+1) % len(pts)], (0,255,0), 3)

    show_image(img)


# ---------------- GÖRSELİ GUI İÇİNDE GÖSTER ---------------- #

def show_image(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_pil.thumbnail((350, 250))

    img_tk = ImageTk.PhotoImage(img_pil)
    image_label.config(image=img_tk)
    image_label.image = img_tk


# ---------------- DOSYA SEÇ ---------------- #

def select_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
    )
    if file_path:
        read_qr(file_path)


# ---------------- SÜRÜKLE BIRAK ---------------- #

def drop(event):
    file_path = event.data

    if file_path.startswith("{") and file_path.endswith("}"):
        file_path = file_path[1:-1]

    read_qr(file_path)


# ---------------- GUI ---------------- #

root = TkinterDnD.Tk()
root.title("QR Kod Okuyucu")
root.geometry("500x600")
root.resizable(False, False)
root.configure(bg="#121212")

style = ttk.Style()
style.theme_use("clam")

style.configure("TButton",
                background="#00C853",
                foreground="white",
                padding=6,
                font=("Segoe UI", 10, "bold"))

# Başlık
title_label = ttk.Label(root,
                        text="QR Kod Okuyucu",
                        font=("Segoe UI", 18, "bold"),
                        background="#121212",
                        foreground="white")
title_label.pack(pady=15)

# Sürükle alanı
drop_label = ttk.Label(root,
                       text="📥 QR görselini buraya sürükle",
                       anchor="center",
                       background="#1e1e1e",
                       foreground="white",
                       font=("Segoe UI", 11))
drop_label.pack(pady=10, ipadx=20, ipady=20)

drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind('<<Drop>>', drop)

# Hover efekti
def on_enter(e):
    drop_label.configure(background="#2a2a2a")

def on_leave(e):
    drop_label.configure(background="#1e1e1e")

drop_label.bind("<Enter>", on_enter)
drop_label.bind("<Leave>", on_leave)

# Dosya seç butonu
select_btn = ttk.Button(root, text="Dosya Seç", command=select_file)
select_btn.pack(pady=10)

# Görsel alanı
image_label = ttk.Label(root, background="#121212")
image_label.pack(pady=10)

# Çıktı kutusu
output_box = Text(root,
                  height=8,
                  bg="#1e1e1e",
                  fg="white",
                  insertbackground="white",
                  relief="flat",
                  bd=0,
                  font=("Consolas", 10))
output_box.pack(padx=20, pady=15, fill="both")

root.mainloop()
