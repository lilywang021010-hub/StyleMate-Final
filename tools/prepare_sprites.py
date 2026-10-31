"""Export atlas regions to GIF for Tk 8.5 compatibility.

Development-only utility; running StyleMate does not require Pillow.
The source art is generated with imagegen; this only slices/resizes its regions.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / 'assets' / 'pixel'
atlas = Image.open(ROOT / 'character-atlas.png').convert('RGB')
CENTERS = [176, 414, 650, 890, 1120, 1356]
WIDTH = 248


def export(region, filename, size):
    # Atlas cells have generous gutters, except the wide evening gown.
    # Keep adjacent sprites out of narrow garments' crop rectangles.
    left, top, right, bottom = region
    wide_gown = filename.startswith('women_') and '_3.' in filename
    inset = 0 if wide_gown else 20
    content = atlas.crop((left + inset, top, right - inset, bottom))
    content = content.resize((size[0] - inset * 2, size[1]), Image.Resampling.NEAREST)
    image = Image.new('RGB', size, '#fcf2f7')
    image.paste(content, (inset, 0))
    image.save(ROOT / filename, 'GIF')
    return image


for gender in ['women', 'men']:
    for index, center in enumerate(CENTERS):
        left, right = center - WIDTH // 2, center + WIDTH // 2
        if gender == 'women':
            waist = [220, 212, 218, 220, 224, 210][index]
            ankle = [456, 465, 455, 452, 453, 454][index]
            bounds = {'head': (0, 136), 'top': (136, waist),
                      'bottom': (waist, ankle), 'shoes': (ankle, 500), 'dress': (136, 500)}
            heights = {'head': 136, 'top': 88, 'bottom': 234, 'shoes': 48, 'dress': 370}
        else:
            waist = [758, 758, 740, 772, 758, 774][index]
            bounds = {'head': (508, 622), 'top': (622, waist),
                      'bottom': (waist, 950), 'shoes': (950, 998)}
            heights = {'head': 124, 'top': 144, 'bottom': 190, 'shoes': 48}
        for category, (top, bottom) in bounds.items():
            if category == 'dress' and index not in [3, 5]:
                continue
            image = export((left, top, right, bottom), f'{gender}_{category}_{index}.gif',
                           (WIDTH, heights[category]))
            if category != 'head':
                # Cards show the garment region, rather than a miniature full person.
                crop = image.crop((28, 0, WIDTH - 28, image.height))
                crop.thumbnail((132, 104), Image.Resampling.NEAREST)
                crop.save(ROOT / f'{gender}_{category}_{index}_thumb.gif', 'GIF')
print('Sprite regions exported to', ROOT)
