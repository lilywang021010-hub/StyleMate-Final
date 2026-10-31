"""Development regression check for catalogue artwork (requires Pillow)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageStat
import stylemate as model
import dressup_ui as ui


def path_for(name, gender, category, thumbnail=False):
    collection, index = ui.art_spec({'name': name, 'category': category, 'occasion': 'casual'}, gender)
    folder = ui.ART if collection == 'base' else ui.ART / collection
    suffix = '_thumb' if thumbnail else ''
    return folder / f'{gender}_{category}_{index}{suffix}.gif'


def check():
    wardrobe = model.load_data('wardrobe.json', [], model.valid_clothing)
    for gender in ['women', 'men']:
        for item in wardrobe:
            if item['gender'] not in [gender, 'unisex']:
                continue
            assert item['name'].lower() in ui.ART_CATALOG[gender], item['name']
            for thumb in [False, True]:
                with Image.open(path_for(item['name'], gender, item['category'], thumb)) as image:
                    image.load()
    pairs = [
        ('women', 'top', 'Red T-shirt', 'White T-shirt'),
        ('women', 'bottom', 'Black jeans', 'Blue jeans'),
        ('women', 'top', 'Pink knit sweater', 'Silk date blouse'),
        ('women', 'dress', 'Red party dress', 'Long wedding gown'),
        ('men', 'top', 'Red T-shirt', 'Navy T-shirt'),
        ('men', 'bottom', 'Black jeans', 'Blue jeans'),
    ]
    for gender, category, first, second in pairs:
        for thumb in [False, True]:
            a = Image.open(path_for(first, gender, category, thumb)).convert('RGB')
            b = Image.open(path_for(second, gender, category, thumb)).convert('RGB')
            assert a.tobytes() != b.tobytes(), (first, second)
    red = Image.open(path_for('Red T-shirt', 'women', 'top')).convert('RGB')
    white = Image.open(path_for('White T-shirt', 'women', 'top')).convert('RGB')
    r = ImageStat.Stat(red.crop((90, 20, 160, 60))).mean
    w = ImageStat.Stat(white.crop((90, 20, 160, 60))).mean
    assert r[0] > r[1] * 2 and r[0] > r[2] * 2, r
    assert min(w) > 170 and max(w) - min(w) < 45, w
    print(f'PASS: {len(wardrobe)} catalogue records; thumbnails and stage sprites; six distinct garment pairs; red/white colour checks.')
    print('Red shirt RGB mean:', [round(v) for v in r], '; white shirt:', [round(v) for v in w])


if __name__ == '__main__':
    check()
