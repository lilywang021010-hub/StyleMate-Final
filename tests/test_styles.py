import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import stylemate as model


def item(name, category, styles, occasion='casual'):
    return dict(name=name, category=category, gender='women', weather='any', occasion=occasion, styles=styles)


class StyleMatchingTests(unittest.TestCase):
    def setUp(self):
        self.wardrobe = [
            item('Red T-shirt', 'top', ['casual', 'sporty']),
            item('White T-shirt', 'top', ['casual', 'minimal']),
            item('Blue jeans', 'bottom', ['casual', 'minimal']),
            item('White sneakers', 'shoes', ['casual', 'minimal', 'sporty']),
        ]

    def test_style_changes_recommendation(self):
        outfit, missing = model.choose_outfit(self.wardrobe, 'dry', 'casual', 'women', 'minimal')
        self.assertEqual(missing, [])
        self.assertEqual(outfit['top']['name'], 'White T-shirt')
        self.assertTrue(all('minimal' in piece['styles'] for piece in outfit.values()))

    def test_no_silent_fallback_when_style_is_missing(self):
        outfit, missing = model.choose_outfit(self.wardrobe, 'dry', 'casual', 'women', 'sporty')
        self.assertEqual(outfit['top']['name'], 'Red T-shirt')
        self.assertEqual(missing, ['bottom'])

    def test_any_style_keeps_other_constraints(self):
        outfit, missing = model.choose_outfit(self.wardrobe, 'rainy', 'casual', 'women', 'any')
        self.assertFalse(missing)
        self.assertFalse(model.matches_plan(self.wardrobe[0], 'dry', 'formal', 'women', 'any'))
        self.assertFalse(model.matches_plan(self.wardrobe[0], 'dry', 'casual', 'men', 'any'))

    def test_dress_only_needs_matching_shoes(self):
        pieces = [item('Gown', 'dress', ['elegant']), item('Sneakers', 'shoes', ['sporty'])]
        outfit, missing = model.choose_outfit(pieces, 'dry', 'casual', 'women', 'elegant')
        self.assertEqual(set(outfit), {'dress'})
        self.assertEqual(missing, ['shoes'])

    def test_saved_style_and_tags_are_independent_snapshots(self):
        outfit, _ = model.choose_outfit(self.wardrobe, 'dry', 'casual', 'women', 'minimal')
        entry = model.history_entry(outfit, 'dry', 'casual', 'women', 'minimal')
        outfit['top']['styles'].clear()
        self.assertEqual(entry['style'], 'minimal')
        self.assertIn('minimal', entry['outfit']['top']['styles'])
        self.assertTrue(model.valid_history(entry))
        with tempfile.TemporaryDirectory() as directory, patch.object(model, 'BASE_DIR', Path(directory)):
            model.save_data('outfit_history.json', [entry])
            self.assertEqual(model.load_data('outfit_history.json', [], model.valid_history), [entry])

    def test_legacy_files_load_without_losing_items(self):
        legacy = [{key: value for key, value in piece.items() if key not in ['styles', 'gender']}
                  for piece in self.wardrobe]
        entry = dict(date='2026-10-24T12:00:00', weather='dry', occasion='casual',
                     outfit={piece['category']: piece for piece in legacy[1:]})
        with tempfile.TemporaryDirectory() as directory, patch.object(model, 'BASE_DIR', Path(directory)):
            (model.BASE_DIR / 'wardrobe.json').write_text(json.dumps(legacy))
            (model.BASE_DIR / 'outfit_history.json').write_text(json.dumps([entry]))
            loaded = model.load_data('wardrobe.json', [], model.valid_clothing)
            history = model.load_data('outfit_history.json', [], model.valid_history)
            self.assertEqual([piece['name'] for piece in loaded], [piece['name'] for piece in legacy])
            self.assertEqual(history[0]['style'], 'any')
            self.assertTrue(all(piece['styles'] for piece in loaded))

    def test_invalid_or_empty_styles_rejected(self):
        self.assertFalse(model.valid_clothing(item('Bad', 'top', [])))
        self.assertFalse(model.valid_clothing(item('Bad', 'top', ['unknown'])))
        self.assertFalse(model.valid_clothing(item('Bad', 'top', 'minimal')))


if __name__ == '__main__':
    unittest.main()
