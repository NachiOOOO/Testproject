import tkinter as tk
from tkinter import colorchooser, messagebox
import colorsys

# --------------------------------------------------
# 光源による色変化シミュレーター（tkinter）
# --------------------------------------------------

LIGHTS = {
    "自然光": {"color": "#FFF1D6", "strength": 0.95},
    "白色照明の室内":     {"color": "#F5F3FF", "strength": 0.95},
    "暖色の室内": {"color": "#FFB45C", "strength": 0.90},
    "夕方":             {"color": "#FF784D", "strength": 0.62},
    "日陰":   {"color": "#9CBDEB", "strength": 0.68},
    "月明かり": {"color": "#526FA8", "strength": 0.28},
    "緑蛍光灯": {"color": "#C8E8B0", "strength": 0.82},
}

def hex_to_rgb(value):
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError("色コードは #D99A78 のような6桁のHEX形式で入力してください。")
    try:
        return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        raise ValueError("色コードに使えるのは0〜9、A〜Fです。")

def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(
        *(max(0, min(255, round(v))) for v in rgb)
    )

def srgb_to_linear(v):
    v = v / 255.0
    if v <= 0.04045:
        return v / 12.92
    return ((v + 0.055) / 1.055) ** 2.4

def linear_to_srgb(v):
    v = max(0.0, min(1.0, v))
    if v <= 0.0031308:
        v = 12.92 * v
    else:
        v = 1.055 * (v ** (1 / 2.4)) - 0.055
    return v * 255.0

def simulate_color(base_hex, light_hex, brightness, light_strength):
    """
    イラスト向けの簡易色変換。
    光源の色味と明るさを分けて処理する。
    """

    base_rgb = hex_to_rgb(base_hex)
    light_rgb = hex_to_rgb(light_hex)

    # RGBを0〜1に変換
    base = [v / 255.0 for v in base_rgb]
    light = [v / 255.0 for v in light_rgb]

    # 元色と光源色をHLSに変換
    base_h, base_l, base_s = colorsys.rgb_to_hls(*base)
    light_h, light_l, light_s = colorsys.rgb_to_hls(*light)

    # 光源の色味を反映する強さ
    tint = 0.35 * light_strength

    # 色相を光源側へ寄せる
    # 色相は円環なので、最短方向に移動する
    hue_diff = (light_h - base_h + 0.5) % 1.0 - 0.5
    new_h = (base_h + hue_diff * tint) % 1.0

    # 彩度は少し抑え、照明下の色の変化を表現
    new_s = base_s * (1.0 - 0.20 * tint)

    # 明るさはスライダーに応じて緩やかに変える
    # 49%でも極端に暗くならないようにする
    exposure = 0.78 + 0.22 * brightness
    new_l = max(0.0, min(1.0, base_l * exposure))

    # HLSからRGBへ戻す
    result = colorsys.hls_to_rgb(new_h, new_l, new_s)

    return rgb_to_hex([v * 255 for v in result])


class ColorSimulator:
    def __init__(self, root):
        self.root = root
        root.title("色覚シミュレーター")
        root.geometry("620x650")
        root.minsize(560, 600)
        root.configure(bg="#F3F4F6")

        self.base_color = tk.StringVar(value="#D99A78")
        self.light_name = tk.StringVar(value="月明かり・夜の屋外")
        self.brightness = tk.DoubleVar(value=75)

        title = tk.Label(
            root, text="光源による色変化シミュレーター",
            font=("Yu Gothic UI", 16, "bold"),
            bg="#F3F4F6", fg="#222222"
        )
        title.pack(pady=(18, 4))

        subtitle = tk.Label(
            root, text="入力:元の色+照明環境",
            font=("Yu Gothic UI", 9), bg="#F3F4F6", fg="#555555"
        )
        subtitle.pack(pady=(0, 14))

        panel = tk.Frame(root, bg="white", padx=18, pady=14)
        panel.pack(fill="x", padx=20, pady=5)

        tk.Label(panel, text="① 元の肌色（HEXカラーコード）",
                 font=("Yu Gothic UI", 10, "bold"),
                 bg="white").pack(anchor="w")

        input_row = tk.Frame(panel, bg="white")
        input_row.pack(fill="x", pady=(8, 4))

        self.color_entry = tk.Entry(
            input_row, textvariable=self.base_color,
            font=("Consolas", 12), width=14
        )
        self.color_entry.pack(side="left", padx=(0, 8))

        tk.Button(input_row, text="色を選ぶ…", command=self.choose_color)\
            .pack(side="left")
        tk.Button(input_row, text="肌色サンプル", command=self.reset_color)\
            .pack(side="left", padx=8)

        tk.Label(panel, text="② 光源・環境を選択",
                 font=("Yu Gothic UI", 10, "bold"),
                 bg="white").pack(anchor="w", pady=(12, 4))

        self.light_menu = tk.OptionMenu(
            panel, self.light_name, *LIGHTS.keys(),
            command=lambda _value: self.update_preview()
        )
        self.light_menu.config(font=("Yu Gothic UI", 10), width=24)
        self.light_menu.pack(anchor="w")

        tk.Label(panel, text="③ 明るさ",
                 font=("Yu Gothic UI", 10, "bold"),
                 bg="white").pack(anchor="w", pady=(12, 0))

        brightness_row = tk.Frame(panel, bg="white")
        brightness_row.pack(fill="x")

        self.brightness_scale = tk.Scale(
            brightness_row, from_=10, to=100, orient="horizontal",
            variable=self.brightness, command=lambda _v: self.update_preview(),
            showvalue=False, bg="white", highlightthickness=0,
            troughcolor="#DDE3EA"
        )
        self.brightness_scale.pack(side="left", fill="x", expand=True)

        self.brightness_label = tk.Label(
            brightness_row, text="75%", width=5, bg="white",
            font=("Yu Gothic UI", 10)
        )
        self.brightness_label.pack(side="right")

        swatches = tk.Frame(root, bg="#F3F4F6")
        swatches.pack(fill="both", expand=True, padx=20, pady=14)

        for col, label in enumerate(("元の色", "変化後の参考色")):
            swatches.columnconfigure(col, weight=1)
            tk.Label(
                swatches, text=label, bg="#F3F4F6",
                font=("Yu Gothic UI", 11, "bold")
            ).grid(row=0, column=col, pady=(0, 8))

        self.original_swatch = tk.Label(
            swatches, text="", bg=self.base_color.get(),
            relief="flat", height=8
        )
        self.original_swatch.grid(row=1, column=0, sticky="nsew", padx=(0, 7))

        self.result_swatch = tk.Label(
            swatches, text="", bg="#777777", relief="flat", height=8
        )
        self.result_swatch.grid(row=1, column=1, sticky="nsew", padx=(7, 0))

        self.original_code = tk.Label(
            swatches, text=self.base_color.get(), bg="#F3F4F6",
            font=("Consolas", 12)
        )
        self.original_code.grid(row=2, column=0, pady=8)

        self.result_code = tk.Label(
            swatches, text="#777777", bg="#F3F4F6",
            font=("Consolas", 12, "bold")
        )
        self.result_code.grid(row=2, column=1, pady=8)

        button_row = tk.Frame(root, bg="#F3F4F6")
        button_row.pack(pady=(0, 12))

        tk.Button(
            button_row, text="色を再計算", command=self.update_preview,
            font=("Yu Gothic UI", 10), padx=12, pady=5
        ).pack(side="left", padx=5)

        tk.Button(
            button_row, text="結果のHEXをコピー", command=self.copy_result,
            font=("Yu Gothic UI", 10), padx=12, pady=5
        ).pack(side="left", padx=5)

        self.note = tk.Label(
            root,
            text="※作画用の簡易近似です。実際の見え方は周囲の色や画面環境でも変わります。",
            bg="#F3F4F6", fg="#666666", font=("Yu Gothic UI", 8),
            wraplength=570
        )
        self.note.pack(pady=(0, 14))

        self.color_entry.bind("<Return>", lambda _event: self.update_preview())
        self.update_preview()

    def choose_color(self):
        chosen = colorchooser.askcolor(
            color=self.base_color.get(), title="元の色を選択"
        )
        if chosen and chosen[1]:
            self.base_color.set(chosen[1].upper())
            self.update_preview()

    def reset_color(self):
        self.base_color.set("#D99A78")
        self.update_preview()

    def update_preview(self):
        self.brightness_label.config(text=f"{int(self.brightness.get())}%")
        try:
            base = rgb_to_hex(hex_to_rgb(self.base_color.get()))
            light = LIGHTS[self.light_name.get()]
            result = simulate_color(
                base, light["color"],
                self.brightness.get() / 100.0,
                light["strength"]
            )
        except (ValueError, KeyError) as error:
            self.result_code.config(text="入力を確認してください")
            self.result_swatch.config(bg="#FFFFFF")
            self.note.config(text=str(error), fg="#B00020")
            return

        self.base_color.set(base)
        self.original_swatch.config(bg=base)
        self.result_swatch.config(bg=result)
        self.original_code.config(text=base)
        self.result_code.config(text=result)
        self.note.config(
            text=f"選択中：{self.light_name.get()}（光源色 {light['color']}）"
                 "｜作画用の簡易近似です。",
            fg="#666666"
        )
        self.last_result = result

    def copy_result(self):
        if not hasattr(self, "last_result"):
            self.update_preview()
        if hasattr(self, "last_result"):
            self.root.clipboard_clear()
            self.root.clipboard_append(self.last_result)
            self.root.update()
            messagebox.showinfo("コピーしました", f"{self.last_result} をコピーしました。")

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorSimulator(root)
    root.mainloop()
