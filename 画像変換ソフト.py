import os
import sys
import ctypes
import tkinter as tk
import tkinter.filedialog as fd
from tkinter import colorchooser, messagebox
import PIL.Image
from PIL import Image, ImageDraw, ImageTk

# --- タスクバーのアイコンを固定する設定 ---
try:
    myappid = 'my_custom_app_id_1234' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

# グローバル変数で選択された色を保持
selected_rgb = None

def dispPhoto(fpath, k_k, value, dark_mode, sirokuro_mode):
    global selected_rgb
    
    # モザイク度の計算
    b = value
    d = b + 1
    e = 9 - d
    c = 2**e
    
    # 画像読み込み (RGBAモードで開くことで色合成を可能にする)
    newImage = PIL.Image.open(fpath).convert("RGBA")
    w, h = newImage.size
    
    f = int(w/(300/c))
    g = int(h/(300/c))
    k = int(w/2)
    l = int(h/2)

    # 1. モザイク処理 (リサイズによる擬似モザイク)
    if value > 0:
        newImage = newImage.resize((f, g), resample=PIL.Image.NEAREST).resize((w, h), resample=PIL.Image.NEAREST)

    # 2. 【追加機能】色をかぶせる処理
    if selected_rgb:
        # 提示されたアルゴリズム：RGBAレイヤーを作成して合成
        alpha = 100 # 透明度(0-255)
        color_layer = PIL.Image.new("RGBA", newImage.size, selected_rgb + (alpha,))
        newImage = PIL.Image.alpha_composite(newImage, color_layer)

    # 3. ダークモード（グレー）・白黒モード処理
    if dark_mode:
        if sirokuro_mode:
            newImage = newImage.convert("L").convert("1")
        else:
            newImage = newImage.convert("L")
    else:
        if sirokuro_mode:
            newImage = newImage.convert("1")

    # 表示用データの作成
    # プレビューは少し小さめに表示（元のコードのk, lサイズを意識）
    previewImage = newImage.resize((k, l))
    imageData = PIL.ImageTk.PhotoImage(previewImage)
    imageLabel.configure(image=imageData)
    imageLabel.image = imageData
    
    # 保存処理 (元のコードの保存ロジックを維持)
    user_home = os.path.expanduser("~")
    debiru = os.path.join(user_home, "Downloads", k_k + '.png')
    
    # 保存時はRGBAからRGBに戻す（互換性のため）
    newImage.convert("RGB").save(debiru)

def openFile():
    fpath = fd.askopenfilename()
    if fpath:
        # 現在の値を渡す
        update_display(fpath)

def update_display(fpath=None):
    """現在の設定で画像を再描画する補助関数"""
    # ファイルパスが渡されない場合は、最後に開いたファイルを使用
    global last_fpath
    if fpath: last_fpath = fpath
    
    if 'last_fpath' in globals():
        value = scale.get()
        k_k = entry.get()
        dark_mode = var1.get()
        sirokuro_mode = var2.get()
        dispPhoto(last_fpath, k_k, value, dark_mode, sirokuro_mode)

def choose_color():
    global selected_rgb
    color = colorchooser.askcolor(title="色を選択する")
    if color[0]:
        selected_rgb = tuple(map(int, color[0])) # (R, G, B)を保存
        lbl["text"] = color[1]
        # 色を選んだら即座に反映
        if 'last_fpath' in globals():
            update_display()

def modosu_color():
    global selected_rgb
    selected_rgb = None
    lbl.configure(text="ここに色が出るよ")
    if 'last_fpath' in globals():
        update_display()

root = tk.Tk()
root.title("画像変換ソフト")
root.geometry("500x650") # 下の方が見切れないよう少しだけ高さを調整

# --- アイコン設定 ---
iconfile = "pixil-frame-0__4_.ico"
icon_path = os.path.join(sys._MEIPASS, iconfile) if getattr(sys, "frozen", False) else iconfile
try:
    root.iconbitmap(icon_path)
except:
    pass

var = tk.IntVar()
var1 = tk.BooleanVar()
var2 = tk.BooleanVar()

# 元のプログラムと同じ順番で配置
btn = tk.Button(text="ファイルを開く", command=openFile)
scale = tk.Scale(root, from_=0, to=7, orient=tk.HORIZONTAL, variable=var)
checkbox = tk.Checkbutton(root, text="ダークモード", variable=var1)
checkbox2 = tk.Checkbutton(root, text="白黒モード", variable=var2)
unco = tk.Button(text="色をかぶせる", command=choose_color)
lbl = tk.Label(text="ここに色が出るよ")
yaju = tk.Button(text="色を初期化する", command=modosu_color)
imageLabel = tk.Label()
entry = tk.Entry(root, width=30)
entry.insert(0, "ここに画像の名前を入力")

# パックする順番も維持
btn.pack()
scale.pack()
checkbox.pack()
checkbox2.pack()
unco.pack()
lbl.pack()
yaju.pack()
imageLabel.pack()
entry.pack()

root.mainloop()