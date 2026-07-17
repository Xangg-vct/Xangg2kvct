# ECU PINOUT TOOL

A desktop app for looking up ECU pinouts by car brand / ECU model, modeled
after the "MEDC17 EGPT PINOUT TOOL" interface: a category tree on the left,
connector image + pin labels on the right, with image zoom/pan support.

## 1. Run on your machine (Windows/Mac/Linux)

Requires Python 3.9+ (Windows: download at https://www.python.org/downloads,
remember to tick "Add Python to PATH" during install).

```bash
pip install pillow
python main.py
```

## 2. Project structure

```
pinout_tool/
├─ main.py                # main code, no changes needed to add data
├─ data/
│  ├─ pinouts.json        # list of car brands / ECU models / pin positions
│  └─ images/              # ECU connector images (you add these)
└─ README.md
```

## 3. Adding a new car brand / ECU model / pinout image

No need to edit `main.py`. Just:

1. Drop the connector image (png/jpg) into `data/images/`.
2. Open `data/pinouts.json`, add a new model under the matching brand
   (or add a whole new brand):

```json
"FAL": {
  "label": "FAL",
  "models": {
    "MED17.3.3": {
      "title": "BOSCH_MED17.3.3_IROM_TC1793_EGPT_FAL",
      "version": "v.02.00",
      "subtitle": ["ECU CONNECTOR / CONNETTORE ECU / CONNECTEUR ECU"],
      "image": "images/FAL_MED17_3_3.png",
      "pins": [
        { "x": 0.79, "y": 0.20, "label": "PIN 5, 86 = +12V", "color": "#e74c3c" }
      ]
    }
  }
}
```

- `x`, `y`: **ratio** coordinates (0.0 → 1.0) relative to the original image
  width/height, not pixels — this keeps labels correctly positioned no matter
  the image size. Quick way to find them: open the image in Paint/GIMP, read
  the cursor's pixel coordinates, then divide by the image width/height.
- `color`: hex color for the pin dot + label (e.g. red = power, blue =
  signal, green = CAN...).
- If no image is set yet, the app still runs fine and shows a placeholder
  panel noting the missing image path.

After editing `pinouts.json`, click **File → Reload data** in the app (or
press **F5**) — no need to restart the program.

## 4. Building a Windows .exe (no Python required to run it)

On a Windows machine with Python + pillow installed:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "data;data" --name "ECU_Pinout_Tool" main.py
```

The `.exe` will be in the `dist/` folder. Copying just this `.exe` file is
enough to run it elsewhere, no Python install needed — but if you update
`pinouts.json`/images later, you'll need to rebuild it (or keep `data/` next
to the `.exe` and adjust `main.py` to read from that folder instead of the
bundled copy — ask if you need that workflow).

## 5. Features

- Quick brand/model search in the "Search" box above the category tree.
- Zoom with the mouse wheel or +/- buttons, drag to pan the image, "Reset
  view" button.
- Automatic placeholder when an image isn't available yet.
- Update data without rebuilding the code (F5 to reload).
- **Export to PDF**: press `Ctrl+P`, or File menu → "Export to PDF...", or
  the "Export PDF (Ctrl+P)" button at the bottom. The PDF contains the
  title, version, subtitle, connector image, and all pin labels — redrawn
  independently of the current on-screen zoom/pan, so it's always crisp and
  correctly positioned.
- **Light/dark mode toggle**: button on the right side of the bottom toolbar
  (🌙/☀) switches the whole interface (category tree, header banner, image
  panel) between light and dark mode, no restart needed.
- **Update checker**: automatically checks GitHub Releases for a newer
  version shortly after launch, and also via the "Check for updates" button
  or Help menu. When a newer version is found, the app **downloads the new
  `.exe` directly to your Downloads folder** (with a progress bar) — no
  browser or GitHub page is ever shown to the user. After the download
  finishes, it offers to open the folder so you can run the new installer.

## 6. What you still need to do

Send over (or add yourself following section 3):
- ECU connector images for each model.
- Pin coordinates + labels to annotate.
- The full list of brands/models if it differs from the current scaffold
  (currently pre-built with 25 brands as shown in your screenshot; FAL has
  4 sample models, and MED17.3.3 has 6 sample pins so you can see how it
  works).

## 7. Version management & publishing new releases on GitHub

The project already includes:
- `APP_VERSION` declared in `main.py`.
- The app automatically checks GitHub Releases for a newer version on
  launch (menu **Help → Check for updates...** for a manual check).
- `.github/workflows/build.yml` — automatically builds the `.exe` and
  publishes a Release whenever you push a version tag (no need to run
  PyInstaller yourself).

See the detailed step-by-step guide (creating an account, creating the
repo, pushing code, publishing new versions) in the accompanying
**`HOW_TO_GITHUB.md`** file.
