import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import stylemate as model
from dressup_ui import DressingRoom, complete, wear_item


def clothing(category, gender='women'):
    return dict(name=category, category=category, gender=gender,
                weather='any', occasion='casual', styles=['minimal'])


class OutfitFlowTests(unittest.TestCase):
    def test_shuffle_uses_dress_when_separates_are_incomplete(self):
        wardrobe = [clothing(key) for key in ['dress', 'shoes', 'top']]
        outfit = model.shuffle_outfit(wardrobe, 'women')
        self.assertEqual(set(outfit), {'dress', 'shoes'})

    def test_shuffle_can_choose_either_complete_form(self):
        wardrobe = [clothing(key) for key in model.CATEGORIES]
        for form in [['dress', 'shoes'], ['top', 'bottom', 'shoes']]:
            with patch.object(model.random, 'choice', side_effect=[form] +
                              [next(item for item in wardrobe if item['category'] == key)
                               for key in form]):
                outfit = model.shuffle_outfit(wardrobe, 'women')
            self.assertEqual(set(outfit), set(form))
            self.assertTrue(complete(outfit))

    def test_shuffle_respects_gender_and_accepts_unisex(self):
        wardrobe = [clothing('dress'), clothing('shoes', 'unisex'), clothing('top', 'men')]
        outfit = model.shuffle_outfit(wardrobe, 'women')
        self.assertEqual(set(outfit), {'dress', 'shoes'})
        self.assertTrue(all(item['gender'] != 'men' for item in outfit.values()))

    def test_empty_or_partial_wardrobe_is_safe(self):
        self.assertEqual(model.shuffle_outfit([], 'women'), {})
        outfit = model.shuffle_outfit([clothing('dress')], 'women')
        self.assertEqual(set(outfit), {'dress'})
        self.assertFalse(complete(outfit))

    def test_manual_dress_and_separates_replace_each_other(self):
        original = {key: clothing(key) for key in ['top', 'bottom', 'shoes']}
        dressed = wear_item(original, clothing('dress'))
        self.assertEqual(set(dressed), {'dress', 'shoes'})
        separated = wear_item(dressed, clothing('top'))
        self.assertEqual(set(separated), {'top', 'shoes'})
        self.assertEqual(set(original), {'top', 'bottom', 'shoes'})
        self.assertFalse(complete(separated))

    def test_recommend_keeps_matching_pieces_when_one_is_missing(self):
        room = SimpleNamespace(
            wardrobe=[clothing('top'), clothing('shoes')],
            context=lambda: ('women', 'dry', 'casual', 'minimal'),
            status=Mock(), refresh=Mock())
        DressingRoom.recommend(room)
        self.assertEqual(set(room.outfit), {'top', 'shoes'})
        self.assertIn('bottom', room.status.set.call_args.args[0])
        room.refresh.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
