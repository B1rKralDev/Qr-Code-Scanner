import cv2
import numpy as np
from pyzbar.pyzbar import decode
from tkinter import Text, END, filedialog, messagebox, simpledialog
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import qrcode
import os
import threading

# ---------------- GLOBAL ---------------- #
history = []

# ---------------- CLIPBOARD ---------------- #
def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

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

    # Gelişmiş RAM optimizasyonu
    h, w = img.shape[:2]
    max_size = 800
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        img = cv2.resize(img, None, fx=scale, fy=scale)

    filename = os.path.basename(file_path)
    output_box.insert(END, f"📂 Dosya: {filename}\n\n")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    decoded_objects = decode(gray)

    if not decoded_objects:
        processed = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        decoded_objects = decode(processed)

    if not decoded_objects:
        decoded_objects = decode(img)

    if not decoded_objects:
        output_box.insert(END, "❌ QR kod bulunamadı.\n")
    else:
        all_data = []

        for obj in decoded_objects:
            qr_data = obj.data.decode("utf-8")
            all_data.append(qr_data)
            history.append(qr_data)

            output_box.insert(END, f"✅ QR İçeriği:\n{qr_data}\n\n")

            pts = [(p.x, p.y) for p in obj.polygon]
            for i in range(len(pts)):
                cv2.line(img, pts[i], pts[(i+1) % len(pts)], (0,255,0), 3)

        final_text = "\n".join(all_data)
        copy_to_clipboard(final_text)
        messagebox.showinfo("Kopyalandı", "QR içeriği panoya kopyalandı!")

    show_image(img)

# Thread wrapper (UI donmasın diye)
def threaded_read(file_path):
    threading.Thread(target=read_qr, args=(file_path,), daemon=True).start()

# ---------------- DOSYA SEÇ ---------------- #
def select_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
    )
    if file_path:
        threaded_read(file_path)

# ---------------- DRAG & DROP ---------------- #
def drop(event):
    files = root.tk.splitlist(event.data)
    for file_path in files:
        threaded_read(file_path)

# ---------------- QR OLUŞTUR ---------------- #
def create_qr():
    text = simpledialog.askstring("QR Oluştur", "QR içeriğini gir:")
    if not text:
        return

    qr = qrcode.make(text)

    save_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png")]
    )

    if save_path:
        qr.save(save_path)
        messagebox.showinfo("Başarılı", "QR kod kaydedildi!")

# ---------------- GEÇMİŞ ---------------- #
def show_history():
    if not history:
        messagebox.showinfo("Geçmiş", "Henüz QR okunmadı.")
        return

    history_text = "\n\n".join(history)
    messagebox.showinfo("QR Geçmişi", history_text)

# ---------------- GÖRSEL GÖSTER ---------------- #
def show_image(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)

    pil_img.thumbnail((400, 400))
    tk_img = ImageTk.PhotoImage(pil_img)

    image_label.config(image=tk_img)
    image_label.image = tk_img

# ---------------- GUI ---------------- #
root = TkinterDnD.Tk()
root.title("QR Kod Okuyucu Pro")
root.geometry("500x700")
root.resizable(False, False)
root.configure(bg="#121212")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton",
                background="#00C853",
                foreground="white",
                padding=6,
                font=("Segoe UI", 10, "bold"))

title_label = ttk.Label(root,
                        text="QR Kod Okuyucu Pro",
                        font=("Segoe UI", 18, "bold"),
                        background="#121212",
                        foreground="white")
title_label.pack(pady=15)

drop_label = ttk.Label(root,
                       text="📥 QR görselini buraya sürükle",
                       anchor="center",
                       background="#1e1e1e",
                       foreground="white",
                       font=("Segoe UI", 11))
drop_label.pack(pady=10, ipadx=20, ipady=20)

drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind('<<Drop>>', drop)

drop_label.bind("<Enter>",
                lambda e: drop_label.configure(background="#2a2a2a"))
drop_label.bind("<Leave>",
                lambda e: drop_label.configure(background="#1e1e1e"))

btn_frame = ttk.Frame(root)
btn_frame.pack(pady=10)

ttk.Button(btn_frame, text="Dosya Seç",
           command=select_file).grid(row=0, column=0, padx=5)

ttk.Button(btn_frame, text="QR Oluştur",
           command=create_qr).grid(row=0, column=1, padx=5)

ttk.Button(btn_frame, text="Geçmişi Göster",
           command=show_history).grid(row=0, column=2, padx=5)

image_label = ttk.Label(root, background="#121212")
image_label.pack(pady=10)

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