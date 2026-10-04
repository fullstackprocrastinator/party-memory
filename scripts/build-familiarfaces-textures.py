"""Export the stylised transparent wordmark as a WoW-compatible TGA."""
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
source = Image.open(ROOT / 'assets/branding/familiar-faces-ui/stylised-wordmark.png').convert('RGBA')
source = source.crop(source.getchannel('A').getbbox())
source.thumbnail((504, 120), Image.Resampling.LANCZOS)
image = Image.new('RGBA', (512, 128), (0, 0, 0, 0))
image.paste(source, ((512-source.width)//2, (128-source.height)//2))
destination = ROOT / 'FamiliarFaces/Textures'
destination.mkdir(parents=True, exist_ok=True)
image.save(destination / 'Wordmark.tga', compression=None)
image.save(ROOT / 'assets/branding/familiar-faces-ui/wordmark.png')
