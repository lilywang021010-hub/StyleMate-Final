"""Slice the second imagegen atlas into aligned game sprites; requires Pillow."""
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1] / 'assets' / 'pixel' / 'variants'
atlas = Image.open(ROOT / 'character-atlas.png').convert('RGB')
centers = [176, 414, 650, 890, 1120, 1356]
for gender in ['women', 'men']:
    for index, cx in enumerate(centers):
        if gender == 'women':
            waist = [220, 212, 216, 218, 232, 216][index]
            ankle = [470, 466, 459, 448, 455, 482][index]
            bounds = {'top': (136, waist, 88), 'bottom': (waist, ankle, 234), 'shoes': (ankle, 500, 48)}
        else:
            waist = [762, 758, 740, 740, 758, 774][index]
            ankle = 950
            bounds = {'top': (622, waist, 144), 'bottom': (waist, ankle, 190), 'shoes': (ankle, 998, 48)}
        for category, (top, bottom, height) in bounds.items():
            # Fixed-width gutters prevent neighboring clothes bleeding into the sprite.
            image = Image.new('RGB', (248, height), '#fcf2f7')
            content = atlas.crop((cx-104, top, cx+104, bottom)).resize((208,height), Image.Resampling.NEAREST)
            image.paste(content, (20,0))
            image.save(ROOT / f'{gender}_{category}_{index}.gif', 'GIF')
            thumb=image.crop((28,0,220,height))
            thumb.thumbnail((132,104), Image.Resampling.NEAREST)
            thumb.save(ROOT / f'{gender}_{category}_{index}_thumb.gif', 'GIF')
        if gender == 'women' and index in [3,5]:
            width = 288 if index == 5 else 248
            image=Image.new('RGB',(width,370),'#fcf2f7')
            upper=atlas.crop((cx-width//2,136,cx+width//2,ankle)).resize((width,322),Image.Resampling.NEAREST)
            foot=atlas.crop((cx-width//2,ankle,cx+width//2,500)).resize((width,48),Image.Resampling.NEAREST)
            image.paste(upper,(0,0)); image.paste(foot,(0,322))
            image.save(ROOT / f'women_dress_{index}.gif','GIF')
            image.thumbnail((132,104),Image.Resampling.NEAREST)
            image.save(ROOT / f'women_dress_{index}_thumb.gif','GIF')
print('Exported distinct garment variants.')
