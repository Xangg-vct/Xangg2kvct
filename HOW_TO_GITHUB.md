# Guide: using GitHub as the place to publish software versions

Final goal:
- A GitHub page holding the full source code.
- Every time you ship a new version, you just "tag" it (e.g. `v1.1.0`) →
  GitHub **automatically builds** the `.exe` and publishes it under
  **Releases**.
- The app you're using will **automatically check** for a newer version
  every time it starts.

Follow the steps below in order — no need to know complex commands, using
**GitHub Desktop** (a GUI app, drag-and-drop) is enough.

---

## Step 1 — Create a GitHub account

1. Go to https://github.com/signup
2. Sign up with your email, choose a username (you'll need to remember
   this, e.g. `johndoe123`).
3. Verify your email.

## Step 2 — Create a Repository (code storage)

1. Log into GitHub, click the green **"New"** button (or go to
   https://github.com/new).
2. Fill in:
   - **Repository name**: e.g. `pinout-tool` (no accents, no spaces).
   - **Public** (so anyone can download the .exe) or **Private** (only you
     / invited people can see it) — your choice.
   - Check **"Add a README file"**.
3. Click **Create repository**.
4. Note down the URL: `https://github.com/<username>/pinout-tool`

## Step 3 — Install GitHub Desktop (to push code without typing commands)

1. Download at: https://desktop.github.com
2. Install it, sign in with the GitHub account you created in Step 1.

## Step 4 — Push the whole project to GitHub

1. Open GitHub Desktop → **File → Clone repository**.
2. Select the `pinout-tool` repo you just created → pick a local folder
   (e.g. `Documents/GitHub/pinout-tool`) → **Clone**.
3. Copy every file inside the `pinout_tool` folder mine sent you (main.py,
   README.md, data/, .gitignore, .github/...) and paste them into the
   exact folder you just cloned (keep the same subfolder structure).
4. Back in GitHub Desktop, you'll see the list of changed files on the
   left. In the bottom-left "Summary" box, type e.g. `First version`, then
   click **Commit to main**.
5. Click **Push origin** at the top to push the code to GitHub.
6. Reload `https://github.com/<username>/pinout-tool` in your browser to
   confirm the code is there.

## Step 5 — Point the code to your real username/repo (so update-checking works)

1. Open `main.py` with IDLE or Notepad.
2. Find these 2 lines near the top:
   ```python
   GITHUB_OWNER = "your-github-username"   # <-- change to your GitHub username
   GITHUB_REPO = "pinout-tool"             # <-- change to your repo name
   ```
3. Edit them to match your real username and repo name, e.g.:
   ```python
   GITHUB_OWNER = "johndoe123"
   GITHUB_REPO = "pinout-tool"
   ```
4. Save the file, then repeat Step 4 (commit + push) to push this change
   to GitHub.

## Step 6 — Publish a new version by "tagging" it (GitHub auto-builds the .exe)

Every time you finish editing code and want to ship a new version:

1. Open `main.py`, find the line:
   ```python
   APP_VERSION = "1.0.0"
   ```
   Change it to the new version number, e.g. `"1.1.0"`. Save.
2. Commit + Push this change to GitHub (as in Step 4).
3. In GitHub Desktop, go to the **History** tab, right-click the commit you
   just pushed → **Create Tag...** → type exactly `v1.1.0` (note the **v**
   at the start, matching the number you just set in `APP_VERSION`).
4. Click **Push origin** once more to push the tag.
5. Go to the **Actions** tab on your GitHub page
   (`https://github.com/<username>/pinout-tool/actions`) — you'll see a
   workflow running named **"Build and Release Windows EXE"**. Wait about
   2–3 minutes for it to finish (green checkmark).
6. Once done, go to the **Releases** tab
   (`https://github.com/<username>/pinout-tool/releases`) — you'll see the
   new `v1.1.0` release with an `ECU_Pinout_Tool.exe` file attached,
   ready to share as a download link.

From now on, each new release is just this same loop: bump the version
number → commit/push → create a tag → push the tag → wait for Actions —
no need to install PyInstaller or build the `.exe` yourself, GitHub does
it for you.

## Step 7 — How the app notifies users of a new version

This is automatic, nothing more to do:
- Every time the app opens, after ~1.5 seconds it quietly asks GitHub what
  the latest release in Releases is.
- If that release is newer than the running `APP_VERSION`, the app shows a
  dialog asking the user if they want to open the download page.
- Users can also manually check anytime via **Help → Check for updates...**
  or the "Check for updates" button in the toolbar.
- If there's no internet connection, the app silently skips the check
  (won't bother the user), unless they manually trigger a check.

## Important notes

- The number in `APP_VERSION` (in `main.py`) and the tag name you push on
  GitHub (`v1.1.0`) must match (only differing by the leading `v`).
- Tags must follow the `v<number>.<number>.<number>` format (e.g. `v1.0.0`,
  `v1.2.3`, `v2.0.0`) for the automated GitHub workflow to detect and run.
- If the repo is **Private**, users need to be logged into GitHub to
  download files from Releases. To let anyone download without an
  account, keep the repo **Public**.
