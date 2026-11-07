# Familiar Faces 0.7.0 demonstration gallery

Upload the numbered PNG images as project gallery images. They execute the real addon Lua interface with fictional sample data. Their captions clearly identify them as demonstrations; native WoW icons and input skins are represented by placeholders. They are not live-client screenshots.

1. `01-adventures.png` — adventure history, notes, pins and location timeline.
2. `02-companions.png` — companion profile, shared history, notes and nickname.
3. `03-custom-tags.png` — preset and custom companion tags.
4. `04-settings.png` — the new settings panel and default preferences.
5. `05-recap.png` — the optional end-of-adventure recap.
6. `06-characters.png` — history filtered to one character.
7. `07-hover-reminders.png` — the actual reminder text in a simulated player tooltip.

Full-size gallery PNGs are 1160 pixels wide. The `description-800` folder contains 800-pixel-wide versions for the description editor's narrower image limit. Use the original PNGs for the gallery.

Rebuild with `scripts/create-070-previews.py` and `scripts/render-070-previews.cjs`. Install Pillow and lupa for Python, and Playwright for Node. The renderer uses an installed Chromium browser.
