"""Export a clean serif wordmark as an uncompressed WoW-compatible TGA."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
image = Image.new('RGBA', (1024, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)
font_path = Path('C:/Windows/Fonts/georgia.ttf')
if not font_path.exists():
    raise SystemExit('Georgia font required for this branding export.')
font = ImageFont.truetype(str(font_path), 115)
draw.text((512, 128), 'Familiar Faces', font=font, fill=(244, 193, 99, 255), anchor='mm')
destination = ROOT / 'FamiliarFaces' / 'Textures'
destination.mkdir(parents=True, exist_ok=True)
image.resize((512, 128), Image.Resampling.LANCZOS).save(destination / 'Wordmark.tga', compression=None)
preview = ROOT / 'assets' / 'branding' / 'familiar-faces-ui'
preview.mkdir(parents=True, exist_ok=True)
image.save(preview / 'wordmark.png')
