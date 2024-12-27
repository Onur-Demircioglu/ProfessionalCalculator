import tkinter as tk
from tkinter import ttk, messagebox
import math
from sympy import symbols, diff, integrate, sympify, latex
import re

class ProfesyonelHesapMakinesi:
    def __init__(self):
        self.pencere = tk.Tk()
        self.pencere.title("Profesyonel Hesap Makinesi")
        self.pencere.geometry("600x800")
        self.pencere.configure(bg='#2c3e50')

        # Ana frame
        self.ana_frame = ttk.Frame(self.pencere, padding="10")
        self.ana_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Stil tanımlamaları
        self.stil_olustur()

        # Değişkenler
        self.sonuc_var = tk.StringVar(value="0")
        self.ifade_var = tk.StringVar()
        self.mod = tk.StringVar(value="RAD")
        self.hafiza = 0
        self.gecmis = []

        # Ekranlar
        self.ekranlari_olustur()
        
        # Buton grupları
        self.buton_gruplari = {
            'hafiza': ['MC', 'MR', 'M+', 'M-', 'MS'],
            'fonksiyon': ['sin', 'cos', 'tan', 'log', 'ln'],
            'ileri': ['√', 'x²', 'x³', '1/x', '|x|'],
            'standart': [
                '7', '8', '9', 'DEL', 'AC',
                '4', '5', '6', '*', '/',
                '1', '2', '3', '+', '-',
                '0', '.', '×10ⁿ', '(', ')'
            ],
            'calculus': ['d/dx', '∫dx', 'lim', 'Σ', 'π'],
            'extra': ['x', 'e', 'ans', '=', 'mod']
        }

        # Butonları oluştur
        self.butonlari_olustur()

        # Klavye bağlantıları
        self.klavye_bagla()

    def stil_olustur(self):
        style = ttk.Style()
        style.configure('Ekran.TEntry',
                       font=('Arial', 20),
                       padding=10,
                       background='#34495e')
        
        style.configure('Buton.TButton',
                       font=('Arial', 12),
                       padding=5)
        
        style.configure('Fonksiyon.TButton',
                       background='#3498db')
        
        style.configure('Islem.TButton',
                       background='#e74c3c')

    def ekranlari_olustur(self):
        # Geçmiş ekranı
        self.gecmis_ekran = tk.Text(
            self.ana_frame,
            height=3,
            width=40,
            font=('Arial', 12),
            bg='#34495e',
            fg='white'
        )
        self.gecmis_ekran.grid(row=0, column=0, columnspan=5, pady=5, sticky='nsew')

        # Ana ekran
        self.ekran = ttk.Entry(
            self.ana_frame,
            textvariable=self.sonuc_var,
            justify="right",
            style='Ekran.TEntry'
        )
        self.ekran.grid(row=1, column=0, columnspan=5, pady=5, sticky='nsew')

        # İfade ekranı (türev/integral için)
        self.ifade_ekran = ttk.Entry(
            self.ana_frame,
            textvariable=self.ifade_var,
            justify="left",
            style='Ekran.TEntry'
        )
        self.ifade_ekran.grid(row=2, column=0, columnspan=5, pady=5, sticky='nsew')

    def butonlari_olustur(self):
        row_index = 3
        
        # Hafıza butonları
        for i, text in enumerate(self.buton_gruplari['hafiza']):
            ttk.Button(
                self.ana_frame,
                text=text,
                style='Buton.TButton',
                command=lambda t=text: self.hafiza_islem(t)
            ).grid(row=row_index, column=i, padx=2, pady=2, sticky='nsew')
        row_index += 1

        # Fonksiyon butonları
        for i, text in enumerate(self.buton_gruplari['fonksiyon']):
            ttk.Button(
                self.ana_frame,
                text=text,
                style='Fonksiyon.TButton',
                command=lambda t=text: self.fonksiyon_tikla(t)
            ).grid(row=row_index, column=i, padx=2, pady=2, sticky='nsew')
        row_index += 1

        # İleri fonksiyon butonları
        for i, text in enumerate(self.buton_gruplari['ileri']):
            ttk.Button(
                self.ana_frame,
                text=text,
                style='Fonksiyon.TButton',
                command=lambda t=text: self.fonksiyon_tikla(t)
            ).grid(row=row_index, column=i, padx=2, pady=2, sticky='nsew')
        row_index += 1

        # Standart butonlar
        for i in range(4):
            for j in range(5):
                index = i * 5 + j
                if index < len(self.buton_gruplari['standart']):
                    text = self.buton_gruplari['standart'][index]
                    ttk.Button(
                        self.ana_frame,
                        text=text,
                        style='Buton.TButton',
                        command=lambda t=text: self.buton_tikla(t)
                    ).grid(row=row_index+i, column=j, padx=2, pady=2, sticky='nsew')
        row_index += 4

        # Calculus butonları
        for i, text in enumerate(self.buton_gruplari['calculus']):
            ttk.Button(
                self.ana_frame,
                text=text,
                style='Fonksiyon.TButton',
                command=lambda t=text: self.calculus_islem(t)
            ).grid(row=row_index, column=i, padx=2, pady=2, sticky='nsew')
        row_index += 1

        # Extra butonlar
        for i, text in enumerate(self.buton_gruplari['extra']):
            ttk.Button(
                self.ana_frame,
                text=text,
                style='Buton.TButton',
                command=lambda t=text: self.extra_islem(t)
            ).grid(row=row_index, column=i, padx=2, pady=2, sticky='nsew')

    def klavye_bagla(self):
        self.pencere.bind('<Return>', lambda e: self.hesapla())
        self.pencere.bind('<BackSpace>', lambda e: self.geri_al())
        self.pencere.bind('<Delete>', lambda e: self.temizle())
        
        # Sayılar ve operatörler için
        for key in '0123456789+-*/().':
            self.pencere.bind(key, lambda e, k=key: self.buton_tikla(k))

    def hafiza_islem(self, islem):
        try:
            if islem == 'MC':
                self.hafiza = 0
            elif islem == 'MR':
                self.sonuc_var.set(str(self.hafiza))
            elif islem == 'M+':
                self.hafiza += float(self.sonuc_var.get())
            elif islem == 'M-':
                self.hafiza -= float(self.sonuc_var.get())
            elif islem == 'MS':
                self.hafiza = float(self.sonuc_var.get())
            self.gecmise_ekle(f"Hafıza işlemi: {islem}")
        except Exception as e:
            self.hata_goster(f"Hafıza işlemi hatası: {str(e)}")

    def calculus_islem(self, islem):
        try:
            ifade = self.ifade_var.get()
            x = symbols('x')
            expr = sympify(ifade)
            
            if islem == 'd/dx':
                sonuc = diff(expr, x)
                self.sonuc_var.set(f"d/dx({ifade}) = {sonuc}")
            elif islem == '∫dx':
                sonuc = integrate(expr, x)
                self.sonuc_var.set(f"∫({ifade})dx = {sonuc} + C")
            elif islem == 'lim':
                # Limit özelliği için ek giriş gerekebilir
                pass
            elif islem == 'Σ':
                # Toplam özelliği için ek giriş gerekebilir
                pass
            elif islem == 'π':
                self.sonuc_var.set(str(math.pi))
            
            self.gecmise_ekle(f"Calculus işlemi: {islem}({ifade})")
        except Exception as e:
            self.hata_goster(f"Calculus işlemi hatası: {str(e)}")

    def extra_islem(self, islem):
        if islem == 'x':
            self.ifade_var.set(self.ifade_var.get() + 'x')
        elif islem == 'e':
            self.ifade_var.set(self.ifade_var.get() + str(math.e))
        elif islem == 'ans':
            son_sonuc = self.gecmis[-1] if self.gecmis else "0"
            self.sonuc_var.set(son_sonuc)
        elif islem == '=':
            self.hesapla()
        elif islem == 'mod':
            self.mod.set('DEG' if self.mod.get() == 'RAD' else 'RAD')

    def fonksiyon_tikla(self, fonksiyon):
        try:
            deger = float(self.sonuc_var.get())
            if fonksiyon == 'sin':
                sonuc = math.sin(deger if self.mod.get() == 'RAD' else math.radians(deger))
            elif fonksiyon == 'cos':
                sonuc = math.cos(deger if self.mod.get() == 'RAD' else math.radians(deger))
            elif fonksiyon == 'tan':
                sonuc = math.tan(deger if self.mod.get() == 'RAD' else math.radians(deger))
            elif fonksiyon == 'log':
                sonuc = math.log10(deger)
            elif fonksiyon == 'ln':
                sonuc = math.log(deger)
            elif fonksiyon == '√':
                sonuc = math.sqrt(deger)
            elif fonksiyon == 'x²':
                sonuc = deger ** 2
            elif fonksiyon == 'x³':
                sonuc = deger ** 3
            elif fonksiyon == '1/x':
                sonuc = 1 / deger
            elif fonksiyon == '|x|':
                sonuc = abs(deger)
            
            self.sonuc_var.set(str(round(sonuc, 8)))
            self.gecmise_ekle(f"{fonksiyon}({deger}) = {sonuc}")
        except Exception as e:
            self.hata_goster(f"Fonksiyon hatası: {str(e)}")

    def buton_tikla(self, deger):
        mevcut = self.sonuc_var.get()
        if mevcut == "0" and deger.isdigit():
            self.sonuc_var.set(deger)
        else:
            self.sonuc_var.set(mevcut + deger)

    def hesapla(self):
        try:
            ifade = self.sonuc_var.get()
            sonuc = eval(ifade)
            self.sonuc_var.set(str(sonuc))
            self.gecmise_ekle(f"{ifade} = {sonuc}")
        except Exception as e:
            self.hata_goster(f"Hesaplama hatası: {str(e)}")

    def temizle(self):
        self.sonuc_var.set("0")
        self.ifade_var.set("")

    def geri_al(self):
        mevcut = self.sonuc_var.get()
        self.sonuc_var.set(mevcut[:-1] if len(mevcut) > 1 else "0")

    def gecmise_ekle(self, metin):
        self.gecmis.append(metin)
        self.gecmis = self.gecmis[-3:]  # Son 3 işlemi tut
        self.gecmis_ekran.delete('1.0', tk.END)
        for islem in self.gecmis:
            self.gecmis_ekran.insert(tk.END, islem + '\n')

    def hata_goster(self, mesaj):
        messagebox.showerror("Hata", mesaj)
        self.temizle()

    def baslat(self):
        self.pencere.mainloop()

if __name__ == "__main__":
    hesap_makinesi = ProfesyonelHesapMakinesi()
    hesap_makinesi.baslat()
