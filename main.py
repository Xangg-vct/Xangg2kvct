"""
ECU PINOUT TOOL - Desktop App (Windows/Mac/Linux)
--------------------------------------------------
- Category tree (car brand -> ECU model) on the left.
- Pinout image + pin labels on the right, with zoom/pan support.
- Data is read from data/pinouts.json, images from data/images/.
- No code changes needed to add data: just edit/add entries in pinouts.json
  and drop images into data/images.

Run:
    pip install pillow
    python main.py

Package as a Windows .exe (optional):
    pip install pyinstaller
    pyinstaller --onefile --windowed --add-data "data;data" main.py
"""

import json
import os
import sys
import threading
import urllib.request
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
except ImportError:
    print("Missing Pillow library. Run: pip install pillow")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "pinouts.json")

# ---- Version / GitHub repo info used for the update check ----
# EDIT THE 2 LINES BELOW after creating your real GitHub repo (see HOW_TO_GITHUB.md)
APP_VERSION = "1.0.4"
GITHUB_OWNER = "Xangg-vct"     # <-- already set to the real repo owner
GITHUB_REPO = "Xangg2kvct"     # <-- already set to the real repo name

ACCENT = "#8a7dff"

THEMES = {
    "light": {
        "app_bg": "#f4f5f7",
        "header_bg": "#ffffff",
        "canvas_bg": "#e9eaee",
        "tree_bg": "#ffffff",
        "tree_fg": "#1b1b1b",
        "title_fg": "#1b1b1b",
        "sub_fg": "#444444",
        "btn_bg": "#ffffff",
        "btn_fg": "#1b1b1b",
        "hint_fg": "#555555",
        "toggle_label": "🌙 Dark mode",
    },
    "dark": {
        "app_bg": "#1a1d24",
        "header_bg": "#242832",
        "canvas_bg": "#12141a",
        "tree_bg": "#20242e",
        "tree_fg": "#e8e9ee",
        "title_fg": "#f2f2f6",
        "sub_fg": "#c6c8d4",
        "btn_bg": "#2c3140",
        "btn_fg": "#f0f0f5",
        "hint_fg": "#9aa0b0",
        "toggle_label": "☀ Light mode",
    },
}


class PinoutApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.data = self.load_data()
        self.title(f"{self.data.get('app_title', 'ECU PINOUT TOOL')} v{APP_VERSION}")
        self.geometry("1180x680")
        self.minsize(820, 520)

        self.current_image_pil = None   # original (PIL) image of the model being viewed
        self.current_pins = []
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self._drag_start = None
        self.theme_name = "light"

        self._build_menu()
        self._build_layout()
        self._populate_tree()
        self._apply_theme()

        self.bind_all("<Control-p>", self._print_to_pdf)
        self.bind_all("<Control-P>", self._print_to_pdf)

        # silently check for updates 1.5s after launch, so it doesn't slow down startup
        self.after(1500, lambda: self._check_for_update_async(silent=True))

    # ---------------------------------------------------------- data
    def load_data(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {DATA_FILE}")
            return {"brands": {}}
        except json.JSONDecodeError as e:
            messagebox.showerror("Data error", f"pinouts.json is malformed:\n{e}")
            return {"brands": {}}

    def reload_data(self):
        self.data = self.load_data()
        self._populate_tree()
        self._clear_viewer()

    # ---------------------------------------------------------- menu
    def _build_menu(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Reload data (F5)", command=self.reload_data)
        filemenu.add_separator()
        filemenu.add_command(label="Export to PDF...", accelerator="Ctrl+P",
                              command=self._print_to_pdf)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="How to add data", command=self._show_help)
        helpmenu.add_separator()
        helpmenu.add_command(label="Check for updates...",
                              command=lambda: self._check_for_update_async(silent=False))
        helpmenu.add_command(label="About",
                              command=lambda: messagebox.showinfo(
                                  "About",
                                  f"ECU PINOUT TOOL\nVersion: v{APP_VERSION}\n"
                                  f"Repo: https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}"))
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.config(menu=menubar)
        self.bind("<F5>", lambda e: self.reload_data())

    def _show_help(self):
        messagebox.showinfo(
            "How to add data",
            "1) Put the ECU image file into the data/images/ folder\n"
            "2) Open data/pinouts.json, add a new model under the right brand:\n"
            "   { \"title\": ..., \"version\": ..., \"image\": \"images/file_name.png\",\n"
            "     \"pins\": [ {\"x\":0.5, \"y\":0.5, \"label\":\"PIN..=...\", \"color\":\"#e74c3c\"} ] }\n"
            "   (x, y are 0..1 ratios of image width/height, not pixels)\n"
            "3) Click File > Reload data (or press F5) to refresh without restarting the app."
        )

    # ---------------------------------------------------------- layout
    def _build_layout(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # ---- LEFT: tree panel
        self.left = ttk.Frame(paned, width=260)
        paned.add(self.left, weight=0)

        search_frame = ttk.Frame(self.left)
        search_frame.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._filter_tree())
        ttk.Entry(search_frame, textvariable=self.search_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        self.tree = ttk.Treeview(self.left, show="tree", selectmode="browse")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        vsb = ttk.Scrollbar(self.left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        # ---- RIGHT: header + viewer
        right = ttk.Frame(paned)
        paned.add(right, weight=1)

        self.header = tk.Frame(right, height=90)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)

        self.lbl_title = tk.Label(self.header, text="",
                                   font=("Segoe UI", 13, "bold"), anchor="w",
                                   justify="left")
        self.lbl_title.place(x=20, y=14)

        self.lbl_version = tk.Label(self.header, text="",
                                     font=("Segoe UI", 10))
        self.lbl_version.place(relx=1.0, x=-20, y=16, anchor="ne")

        self.lbl_subtitle = tk.Label(self.header, text="",
                                      font=("Segoe UI", 9),
                                      justify="left")
        self.lbl_subtitle.place(x=20, y=44)

        ttk.Separator(right, orient="horizontal").pack(fill=tk.X)

        self.canvas_wrap = tk.Frame(right)
        self.canvas_wrap.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_wrap, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self._redraw())
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_move)
        self.canvas.bind("<MouseWheel>", self._on_zoom)      # Windows / Mac
        self.canvas.bind("<Button-4>", lambda e: self._on_zoom(e, delta=120))
        self.canvas.bind("<Button-5>", lambda e: self._on_zoom(e, delta=-120))

        zoom_bar = ttk.Frame(right)
        zoom_bar.pack(fill=tk.X)
        ttk.Button(zoom_bar, text="-", width=3,
                   command=lambda: self._zoom_step(-0.1)).pack(side=tk.LEFT, padx=4, pady=4)
        ttk.Button(zoom_bar, text="+", width=3,
                   command=lambda: self._zoom_step(0.1)).pack(side=tk.LEFT)
        ttk.Button(zoom_bar, text="Reset view",
                   command=self._reset_view).pack(side=tk.LEFT, padx=8)
        ttk.Button(zoom_bar, text="Export PDF (Ctrl+P)",
                   command=self._print_to_pdf).pack(side=tk.LEFT, padx=8)

        self.update_btn = ttk.Button(
            zoom_bar, text="Check for updates",
            command=lambda: self._check_for_update_async(silent=False))
        self.update_btn.pack(side=tk.LEFT, padx=8)

        self.theme_btn = ttk.Button(zoom_bar, text="", width=16,
                                     command=self._toggle_theme)
        self.theme_btn.pack(side=tk.RIGHT, padx=8)

        self.lbl_hint = ttk.Label(
            zoom_bar, text="Drag to pan the image, scroll to zoom")
        self.lbl_hint.pack(side=tk.RIGHT, padx=8)

        self._clear_viewer()

    # ---------------------------------------------------------- update check
    def _version_tuple(self, v):
        parts = []
        for p in v.split("."):
            num = "".join(ch for ch in p if ch.isdigit())
            parts.append(int(num) if num else 0)
        return tuple(parts)

    def _check_for_update_async(self, silent=True):
        if not silent:
            self.update_btn.configure(state="disabled", text="Checking...")
        threading.Thread(target=self._check_for_update_worker,
                          args=(silent,), daemon=True).start()

    def _reset_update_btn(self):
        self.update_btn.configure(state="normal", text="Check for updates")

    def _check_for_update_worker(self, silent):
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
        try:
            req = urllib.request.Request(
                url, headers={"Accept": "application/vnd.github+json",
                              "User-Agent": "ECU-Pinout-Tool"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            latest_tag = str(data.get("tag_name", "")).lstrip("vV")
            release_url = data.get(
                "html_url",
                f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases")

            if latest_tag and self._version_tuple(latest_tag) > self._version_tuple(APP_VERSION):
                self.after(0, lambda: self._on_update_available(latest_tag, release_url))
            elif not silent:
                self.after(0, lambda: messagebox.showinfo(
                    "Check for updates", f"You are running the latest version (v{APP_VERSION})."))
        except Exception as e:
            if not silent:
                self.after(0, lambda: messagebox.showwarning(
                    "Check for updates",
                    f"Could not connect to GitHub to check for updates.\n"
                    f"Check your internet connection or try again later.\n\nDetails: {e}"))
        finally:
            if not silent:
                self.after(0, self._reset_update_btn)

    def _on_update_available(self, latest_tag, release_url):
        if messagebox.askyesno(
                "Update available",
                f"A new version is available: v{latest_tag}\n"
                f"You are running: v{APP_VERSION}\n\n"
                "Open the download page now?"):
            webbrowser.open(release_url)

    # ---------------------------------------------------------- theme
    def _apply_theme(self):
        t = THEMES[self.theme_name]
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=t["app_bg"])
        style.configure("TLabel", background=t["app_bg"], foreground=t["tree_fg"])
        style.configure("TButton", background=t["btn_bg"], foreground=t["btn_fg"])
        style.map("TButton", background=[("active", ACCENT)])
        style.configure("TEntry", fieldbackground=t["tree_bg"],
                         foreground=t["tree_fg"])
        style.configure("Treeview", background=t["tree_bg"],
                         fieldbackground=t["tree_bg"], foreground=t["tree_fg"],
                         borderwidth=0)
        style.map("Treeview", background=[("selected", ACCENT)],
                  foreground=[("selected", "#ffffff")])

        self.configure(bg=t["app_bg"])
        self.header.configure(bg=t["header_bg"])
        self.lbl_title.configure(bg=t["header_bg"], fg=t["title_fg"])
        self.lbl_version.configure(bg=t["header_bg"], fg=t["hint_fg"])
        self.lbl_subtitle.configure(bg=t["header_bg"], fg=t["sub_fg"])
        self.canvas_wrap.configure(bg=t["app_bg"])
        self.canvas.configure(bg=t["canvas_bg"])
        self.theme_btn.configure(text=t["toggle_label"])

        self._redraw()

    def _toggle_theme(self):
        self.theme_name = "dark" if self.theme_name == "light" else "light"
        self._apply_theme()

    # ---------------------------------------------------------- print / pdf
    def _get_font(self, size, bold=False):
        candidates = ["arialbd.ttf", "arial.ttf"] if bold else ["arial.ttf"]
        for name in candidates:
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                continue
        return ImageFont.load_default()

    def _build_export_image(self):
        """Redraw the whole view (title + image + pin labels) into a single PIL
        image, independent of the current zoom/pan, for a crisp, well-framed PDF."""
        if self.current_image_pil is None:
            return None

        base = self.current_image_pil.copy()
        w, h = base.size
        header_h = 100
        page = Image.new("RGB", (w, h + header_h), "white")
        draw = ImageDraw.Draw(page)

        font_title = self._get_font(20, bold=True)
        font_sub = self._get_font(13)

        title_text = self.lbl_title.cget("text") or ""
        version_text = self.lbl_version.cget("text") or ""
        subtitle_text = self.lbl_subtitle.cget("text") or ""

        draw.text((24, 16), title_text, fill="#111111", font=font_title)
        if version_text:
            tw = draw.textlength(version_text, font=font_sub)
            draw.text((w - 24 - tw, 18), version_text, fill="#555555", font=font_sub)
        if subtitle_text:
            draw.multiline_text((24, 52), subtitle_text, fill="#333333",
                                 font=font_sub, spacing=4)

        page.paste(base, (0, header_h))

        for pin in self.current_pins:
            px = pin.get("x", 0.5) * w
            py = header_h + pin.get("y", 0.5) * h
            color = pin.get("color", "#e74c3c")
            label = pin.get("label", "")

            r = 6
            draw.ellipse([px - r, py - r, px + r, py + r],
                         fill=color, outline="white", width=2)

            lx, ly = px + 14, py - 10
            bbox = draw.textbbox((lx, ly), label, font=font_sub)
            pad = 5
            draw.rectangle([bbox[0] - pad, bbox[1] - pad,
                            bbox[2] + pad, bbox[3] + pad], fill=color)
            draw.text((lx, ly), label, fill="white", font=font_sub)
            draw.line([px, py, lx - 4, ly], fill=color, width=2)

        return page

    def _print_to_pdf(self, event=None):
        if self.current_image_pil is None:
            messagebox.showinfo("Export PDF", "Please select an ECU model before exporting.")
            return

        page = self._build_export_image()
        if page is None:
            return

        title_text = (self.lbl_title.cget("text") or "pinout").strip()
        safe_name = "".join(c if c.isalnum() or c in "._- " else "_"
                            for c in title_text)[:80] or "pinout"
        path = filedialog.asksaveasfilename(
            title="Save pinout as PDF",
            defaultextension=".pdf",
            initialfile=f"{safe_name}.pdf",
            filetypes=[("PDF files", "*.pdf")])
        if not path:
            return

        try:
            page.save(path, "PDF", resolution=150.0)
            messagebox.showinfo("Export PDF", f"PDF file saved:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save PDF:\n{e}")

    # ---------------------------------------------------------- tree
    def _populate_tree(self, filter_text=""):
        self.tree.delete(*self.tree.get_children())
        filter_text = filter_text.lower().strip()

        root_id = self.tree.insert("", "end", text="CAR BRAND", open=True, iid="ROOT")
        brands = self.data.get("brands", {})
        for brand_key, brand in brands.items():
            label = brand.get("label", brand_key)
            models = brand.get("models", {})

            if filter_text:
                model_matches = {
                    mk: m for mk, m in models.items() if filter_text in mk.lower()
                }
                if filter_text not in label.lower() and not model_matches:
                    continue
                shown_models = model_matches if model_matches else models
            else:
                shown_models = models

            brand_iid = f"BRAND::{brand_key}"
            self.tree.insert(root_id, "end", text=label, iid=brand_iid,
                              open=bool(filter_text))
            for model_key in shown_models:
                model_iid = f"MODEL::{brand_key}::{model_key}"
                self.tree.insert(brand_iid, "end", text=model_key, iid=model_iid)

    def _filter_tree(self):
        self._populate_tree(self.search_var.get())

    def _on_tree_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        if iid.startswith("MODEL::"):
            _, brand_key, model_key = iid.split("::", 2)
            self._load_model(brand_key, model_key)

    # ---------------------------------------------------------- viewer
    def _clear_viewer(self):
        self.lbl_title.config(text="Select an ECU model on the left to view its pinout")
        self.lbl_version.config(text="")
        self.lbl_subtitle.config(text="")
        self.canvas.delete("all")
        self.current_image_pil = None
        self.current_pins = []

    def _load_model(self, brand_key, model_key):
        model = self.data["brands"][brand_key]["models"][model_key]

        self.lbl_title.config(text=model.get("title", model_key))
        self.lbl_version.config(text=model.get("version", ""))
        self.lbl_subtitle.config(text="\n".join(model.get("subtitle", [])))

        image_rel = model.get("image", "")
        image_path = os.path.join(DATA_DIR, image_rel) if image_rel else None

        if image_path and os.path.isfile(image_path):
            self.current_image_pil = Image.open(image_path).convert("RGB")
        else:
            self.current_image_pil = self._placeholder_image(image_rel or "(no image yet)")

        self.current_pins = model.get("pins", [])
        self._reset_view()

    def _placeholder_image(self, missing_path):
        w, h = 900, 500
        img = Image.new("RGB", (w, h), "#dfe1e6")
        draw = ImageDraw.Draw(img)
        draw.rectangle([40, 40, w - 40, h - 40], outline="#9aa0ab", width=3)
        text = "No image for this model yet"
        sub = f"Place the file at: data/{missing_path}"
        draw.text((60, h // 2 - 30), text, fill="#555")
        draw.text((60, h // 2), sub, fill="#888")
        return img

    # ---------------------------------------------------------- zoom/pan
    def _reset_view(self):
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self._redraw()

    def _zoom_step(self, delta):
        self.zoom = max(0.2, min(5.0, self.zoom + delta))
        self._redraw()

    def _on_zoom(self, event, delta=None):
        d = delta if delta is not None else event.delta
        step = 0.1 if d > 0 else -0.1
        self._zoom_step(step)

    def _on_drag_start(self, event):
        self._drag_start = (event.x, event.y)

    def _on_drag_move(self, event):
        if self._drag_start is None:
            return
        dx = event.x - self._drag_start[0]
        dy = event.y - self._drag_start[1]
        self.offset_x += dx
        self.offset_y += dy
        self._drag_start = (event.x, event.y)
        self._redraw()

    def _redraw(self):
        self.canvas.delete("all")
        if self.current_image_pil is None:
            return

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw <= 1 or ch <= 1:
            return

        iw, ih = self.current_image_pil.size
        base_scale = min(cw / iw, ch / ih) * 0.92
        scale = base_scale * self.zoom

        disp_w, disp_h = max(1, int(iw * scale)), max(1, int(ih * scale))
        resized = self.current_image_pil.resize((disp_w, disp_h), Image.LANCZOS)
        self._tk_img = ImageTk.PhotoImage(resized)

        cx = cw // 2 + self.offset_x
        cy = ch // 2 + self.offset_y
        self.canvas.create_image(cx, cy, image=self._tk_img, anchor="center")

        top_left_x = cx - disp_w / 2
        top_left_y = cy - disp_h / 2

        for pin in self.current_pins:
            px = top_left_x + pin.get("x", 0.5) * disp_w
            py = top_left_y + pin.get("y", 0.5) * disp_h
            color = pin.get("color", "#e74c3c")
            label = pin.get("label", "")

            r = 6
            self.canvas.create_oval(px - r, py - r, px + r, py + r,
                                     fill=color, outline="white", width=2)

            lx, ly = px + 14, py - 10
            text_id = self.canvas.create_text(
                lx, ly, text=label, anchor="w", fill="white",
                font=("Segoe UI", 9, "bold"))
            bbox = self.canvas.bbox(text_id)
            if bbox:
                pad = 5
                rect = self.canvas.create_rectangle(
                    bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad,
                    fill=color, outline="")
                self.canvas.tag_lower(rect, text_id)
            self.canvas.create_line(px, py, lx - 4, ly, fill=color, width=2)


if __name__ == "__main__":
    app = PinoutApp()
    app.mainloop()
