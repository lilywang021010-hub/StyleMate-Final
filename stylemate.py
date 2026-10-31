"""StyleMate: a wardrobe manager and outfit planner using Python and Tkinter.

MAIN ENTRY POINT: run `python3 stylemate.py` (Windows: `py stylemate.py`).
Requires Python 3 with working Tk support; run the GUI locally, outside Ed.
Keep dressup_ui.py, wardrobe.json and assets/ beside this file.
For a text-only alternative, run `python3 stylemate.py --terminal`.
See README.txt for dependencies, storage and demonstration instructions.
"""
import json
import random
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTFIT_CATEGORIES = ['top', 'bottom', 'shoes']
CATEGORIES = ['top', 'bottom', 'dress', 'shoes']
GENDERS = ['women', 'men', 'unisex']
WEATHER = ['any', 'dry', 'rainy']
OCCASIONS = ['casual', 'university', 'work', 'formal', 'date', 'party', 'sport', 'wedding', 'beach']
STYLES = ['casual', 'minimal', 'cute', 'sporty', 'elegant']
STYLE_PREFERENCES = ['any'] + STYLES


def default_styles(item):
    """Starter tags for examples and files saved before style tags existed."""
    name = str(item.get('name', '')).lower()
    occasion = item.get('occasion')
    if occasion == 'sport' or any(word in name for word in ['running', 'legging', 'training']):
        return ['sporty']
    if any(word in name for word in ['pink', 'floral', 'silk', 'low heels', 'sundress']):
        return ['casual', 'cute', 'elegant']
    if any(word in name for word in ['gown', 'party dress', 'wedding', 'high heels']):
        return ['elegant']
    if any(word in name for word in ['sneaker', 'canvas']):
        return ['casual', 'minimal', 'cute', 'sporty']
    if any(word in name for word in ['jeans', 'chinos', 'trousers']):
        return ['casual', 'minimal', 'cute', 'elegant']
    if 'red t-shirt' in name:
        return ['casual', 'sporty']
    if occasion in ['work', 'formal', 'date', 'party', 'wedding']:
        return ['minimal', 'elegant']
    return ['casual', 'minimal']


def sample_wardrobe():
    examples = [
        ('women', 'top', 'White T-shirt', 'dry', 'casual'),
        ('women', 'bottom', 'Blue jeans', 'any', 'casual'),
        ('women', 'shoes', 'White sneakers', 'dry', 'casual'),
        ('women', 'top', 'Pink knit sweater', 'any', 'university'),
        ('women', 'bottom', 'Black jeans', 'any', 'university'),
        ('women', 'shoes', 'Canvas sneakers', 'dry', 'university'),
        ('women', 'top', 'Cream blouse', 'any', 'work'),
        ('women', 'bottom', 'Black work trousers', 'any', 'work'),
        ('women', 'shoes', 'Black leather shoes', 'any', 'work'),
        ('women', 'top', 'White blouse', 'any', 'formal'),
        ('women', 'bottom', 'Navy trousers', 'any', 'formal'),
        ('women', 'shoes', 'Black heels', 'any', 'formal'),
        ('women', 'top', 'Silk date blouse', 'dry', 'date'),
        ('women', 'bottom', 'Long floral skirt', 'dry', 'date'),
        ('women', 'shoes', 'Low heels', 'dry', 'date'),
        ('women', 'dress', 'Red party dress', 'dry', 'party'),
        ('women', 'shoes', 'Silver high heels', 'dry', 'party'),
        ('women', 'top', 'Sport T-shirt', 'dry', 'sport'),
        ('women', 'bottom', 'Black leggings', 'dry', 'sport'),
        ('women', 'shoes', 'Running shoes', 'dry', 'sport'),
        ('women', 'dress', 'Long wedding gown', 'any', 'wedding'),
        ('women', 'shoes', 'Ivory wedding heels', 'any', 'wedding'),
        ('women', 'dress', 'Yellow beach sundress', 'dry', 'beach'),
        ('women', 'shoes', 'Brown sandals', 'dry', 'beach'),
        ('men', 'top', 'Navy T-shirt', 'dry', 'casual'),
        ('men', 'bottom', 'Khaki shorts', 'dry', 'casual'),
        ('men', 'shoes', 'White sneakers', 'dry', 'casual'),
        ('men', 'top', 'Blue sweatshirt', 'any', 'university'),
        ('men', 'bottom', 'Blue jeans', 'any', 'university'),
        ('men', 'shoes', 'Canvas sneakers', 'dry', 'university'),
        ('men', 'top', 'White work shirt', 'any', 'work'),
        ('men', 'bottom', 'Charcoal chinos', 'any', 'work'),
        ('men', 'shoes', 'Brown leather shoes', 'any', 'work'),
        ('men', 'top', 'White formal shirt', 'any', 'formal'),
        ('men', 'bottom', 'Black formal trousers', 'any', 'formal'),
        ('men', 'shoes', 'Black leather shoes', 'any', 'formal'),
        ('men', 'top', 'Casual date shirt', 'dry', 'date'),
        ('men', 'bottom', 'Dark jeans', 'any', 'date'),
        ('men', 'shoes', 'Brown leather shoes', 'dry', 'date'),
        ('men', 'top', 'Party shirt', 'dry', 'party'),
        ('men', 'bottom', 'Black jeans', 'any', 'party'),
        ('men', 'shoes', 'Black leather shoes', 'dry', 'party'),
        ('men', 'top', 'Sport training shirt', 'dry', 'sport'),
        ('men', 'bottom', 'Running shorts', 'dry', 'sport'),
        ('men', 'shoes', 'Running shoes', 'dry', 'sport'),
        ('men', 'top', 'Wedding suit jacket', 'any', 'wedding'),
        ('men', 'bottom', 'Wedding suit trousers', 'any', 'wedding'),
        ('men', 'shoes', 'Polished leather shoes', 'any', 'wedding'),
        ('men', 'top', 'Linen beach shirt', 'dry', 'beach'),
        ('men', 'bottom', 'Linen beach shorts', 'dry', 'beach'),
        ('men', 'shoes', 'Leather sandals', 'dry', 'beach'),
    ]
    clothing = [dict(gender=gender, category=category, name=name,
                 weather=weather, occasion=occasion)
            for gender, category, name, weather, occasion in examples]
    for item in clothing:
        item['styles'] = default_styles(item)
    return clothing


def valid_clothing(item):
    return (isinstance(item, dict)
            and isinstance(item.get('name'), str) and bool(item['name'].strip())
            and item.get('category') in CATEGORIES
            and item.get('gender') in GENDERS
            and item.get('weather') in WEATHER
            and item.get('occasion') in OCCASIONS
            and isinstance(item.get('styles'), list)
            and bool(item['styles'])
            and all(style in STYLES for style in item['styles']))


def valid_history(entry):
    return (isinstance(entry, dict)
            and isinstance(entry.get('date'), str)
            and entry.get('weather') in ['dry', 'rainy']
            and entry.get('occasion') in OCCASIONS
            and entry.get('gender') in GENDERS
            and entry.get('style') in STYLE_PREFERENCES
            and isinstance(entry.get('outfit'), dict)
            and all(valid_clothing(item) for item in entry['outfit'].values())
            and all(item['category'] == category for category, item in entry['outfit'].items())
            and set(entry['outfit']) in [{'dress', 'shoes'}, {'top', 'bottom', 'shoes'}])


def load_data(filename, default, validator):
    try:
        with (BASE_DIR / filename).open(encoding='utf-8') as file:
            data = json.load(file)
        # Older versions did not store gender. Keep those clothes usable as unisex.
        if filename == 'wardrobe.json' and isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item.setdefault('gender', 'unisex')
                    item.setdefault('styles', default_styles(item))
        if filename == 'outfit_history.json' and isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict):
                    entry.setdefault('gender', 'unisex')
                    entry.setdefault('style', 'any')
                    if isinstance(entry.get('outfit'), dict):
                        for item in entry['outfit'].values():
                            if isinstance(item, dict):
                                item.setdefault('gender', 'unisex')
                                item.setdefault('styles', default_styles(item))
        if not isinstance(data, list) or not all(validator(item) for item in data):
            raise ValueError('Incorrect data format')
        return data
    except FileNotFoundError:
        return default
    except (OSError, ValueError) as error:
        raise ValueError(f'Cannot read {filename}: {error}') from error


def save_data(filename, data):
    # Write a temporary file first, so an interrupted write preserves the old file.
    path = BASE_DIR / filename
    temporary = path.with_suffix('.json.tmp')
    with temporary.open('w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    temporary.replace(path)


def matches_plan(item, weather, occasion, gender, style='any'):
    return (item['gender'] in [gender, 'unisex']
            and item['weather'] in ['any', weather]
            and item['occasion'] == occasion
            and (style == 'any' or style in item['styles']))


def choose_outfit(wardrobe, weather, occasion, gender, style='any'):
    outfit = {}
    missing = []
    suitable = [item for item in wardrobe if matches_plan(item, weather, occasion, gender, style)]
    dresses = [item for item in suitable if item['category'] == 'dress']
    shoes = [item for item in suitable if item['category'] == 'shoes']
    if dresses and shoes:
        return {'dress': random.choice(dresses).copy(),
                'shoes': random.choice(shoes).copy()}, []
    if dresses and not shoes:
        return {'dress': random.choice(dresses).copy()}, ['shoes']
    for category in OUTFIT_CATEGORIES:
        matches = [item for item in suitable if item['category'] == category]
        if matches:
            outfit[category] = random.choice(matches).copy()
        else:
            missing.append(category)
    return outfit, missing


def history_entry(outfit, weather, occasion, gender, style='any'):
    return {'date': datetime.now().isoformat(timespec='seconds'),
            'weather': weather, 'occasion': occasion, 'gender': gender, 'style': style,
            'outfit': {key: dict(value, styles=list(value['styles'])) for key, value in outfit.items()}}


def shuffle_outfit(wardrobe, gender):
    """Mix freely, preferring a complete look whenever the wardrobe allows one."""
    available = {category: [item for item in wardrobe
                           if item['category'] == category
                           and item['gender'] in [gender, 'unisex']]
                 for category in CATEGORIES}
    forms = [['top', 'bottom', 'shoes'], ['dress', 'shoes']]
    complete_forms = [form for form in forms if all(available[key] for key in form)]
    if complete_forms:
        categories = random.choice(complete_forms)
    else:
        # Show the closest available combination and let the user fill its gaps.
        categories = min(forms, key=lambda form: sum(not available[key] for key in form))
    return {key: random.choice(available[key]).copy()
            for key in categories if available[key]}


def start_gui(wardrobe, history):
    from dressup_ui import launch
    launch(wardrobe, history)


def start_terminal(wardrobe, history):
    def option(prompt, choices):
        while True:
            answer = input(prompt).strip().lower()
            if answer in choices:
                return answer
            print('Choose from: ' + ', '.join(choices))

    while True:
        print('\nStyleMate\n1. View wardrobe\n2. Add clothing\n3. Remove clothing\n4. Recommend outfit\n5. Outfit history\n0. Exit')
        choice = option('Choose: ', ['0', '1', '2', '3', '4', '5'])
        try:
            if choice == '0':
                return
            if choice == '1':
                if not wardrobe:
                    print('Your wardrobe is empty.')
                for i, item in enumerate(wardrobe, 1):
                    print(f"{i}. {item['name']} | {item['gender']} | {item['category']} | {item['weather']} | {item['occasion']} | {', '.join(item['styles'])}")
            elif choice == '2':
                name = input('Clothing name: ').strip()
                if not name:
                    print('Name cannot be empty.')
                    continue
                item = {'name': name,
                        'gender': option('Gender (women/men/unisex): ', GENDERS),
                        'category': option('Category (top/bottom/dress/shoes): ', CATEGORIES),
                        'weather': option('Weather (any/dry/rainy): ', WEATHER),
                        'occasion': option('Occasion: ', OCCASIONS)}
                while True:
                    styles = input('Styles (comma-separated: casual, minimal, cute, sporty, elegant): ')
                    item['styles'] = list(dict.fromkeys(tag.strip().lower() for tag in styles.split(',')))
                    if valid_clothing(item):
                        break
                    print('Choose at least one of the listed styles.')
                updated = wardrobe + [item]
                save_data('wardrobe.json', updated)
                wardrobe[:] = updated
                print('Added and saved.')
            elif choice == '3':
                for i, item in enumerate(wardrobe, 1):
                    print(f"{i}. {item['name']}")
                try:
                    number = int(input('Number to remove (0 to cancel): '))
                except ValueError:
                    print('Please enter a whole number.')
                    continue
                if number == 0:
                    continue
                if not 1 <= number <= len(wardrobe):
                    print('Invalid number.')
                    continue
                updated = wardrobe.copy()
                updated.pop(number - 1)
                save_data('wardrobe.json', updated)
                wardrobe[:] = updated
                print('Removed and saved.')
            elif choice == '4':
                gender = option('Gender (women/men): ', GENDERS[:2])
                weather = option('Weather (dry/rainy): ', ['dry', 'rainy'])
                occasion = option('Occasion: ', OCCASIONS)
                style = option('Preferred style (any/casual/minimal/cute/sporty/elegant): ', STYLE_PREFERENCES)
                outfit, missing = choose_outfit(wardrobe, weather, occasion, gender, style)
                if missing:
                    print('No matching clothing for: ' + ', '.join(missing) + '. Try style any or another plan.')
                    continue
                for category, item in outfit.items():
                    print(f"{category}: {item['name']}")
                if option('Save outfit (y/n)? ', ['y', 'n']) == 'y':
                    updated = history + [history_entry(outfit, weather, occasion, gender, style)]
                    save_data('outfit_history.json', updated)
                    history[:] = updated
                    print('Outfit saved.')
            elif choice == '5':
                if not history:
                    print('No saved outfits yet.')
                for entry in reversed(history):
                    print(f"{entry['date']} | {entry['gender']} | {entry['weather']} | {entry['occasion']} | Style: {entry['style']}")
                    print(', '.join(item['name'] for item in entry['outfit'].values()))
        except OSError as error:
            print(f'Could not save changes: {error}')


def main():
    try:
        wardrobe = load_data('wardrobe.json', sample_wardrobe(), valid_clothing)
        history = load_data('outfit_history.json', [], valid_history)
    except ValueError as error:
        print(error)
        print('Please repair the data file before restarting. Existing data has been preserved.')
        return
    if '--terminal' in sys.argv:
        try:
            start_terminal(wardrobe, history)
        except (EOFError, KeyboardInterrupt):
            print('\nGoodbye. Completed changes have already been saved.')
    else:
        start_gui(wardrobe, history)


if __name__ == '__main__':
    main()
