"""Optional real-Tk integration checks: python3 tools/check_gui.py.

Requires a local graphical session and Tk 8.6+. Uses hidden windows, temporary
JSON storage and real widgets. Dialog responses are mocked. This does not test
physical mouse/keyboard input or judge the visual layout.
"""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import stylemate as model
from dressup_ui import DressingRoom, complete


class GuiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One Tcl interpreter avoids macOS Tk event-loop issues between tests.
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.addClassCleanup(cls.root.destroy)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='stylemate-gui-check-')
        self.addCleanup(temporary.cleanup)
        self.enterContext(patch.object(model, 'BASE_DIR', Path(temporary.name)))
        self.callback_errors = []
        self.root.report_callback_exception = lambda *error: self.callback_errors.append(error)
        self.room = DressingRoom(self.root, model.sample_wardrobe(), [])
        self.dialogs = {
            name: self.enterContext(patch('dressup_ui.messagebox.' + name))
            for name in ['showinfo', 'showwarning', 'showerror', 'askyesno']}
        self.dialogs['askyesno'].return_value = True
        self.flush()

    def tearDown(self):
        for child in self.root.winfo_children():
            child.destroy()
        self.root.update_idletasks()

    def flush(self):
        self.root.update()
        self.assertEqual(self.callback_errors, [], 'An event callback raised an error')

    def button(self, text):
        """Invoke the command registered on the actual button widget."""
        pending = [self.root]
        while pending:
            widget = pending.pop()
            if widget.winfo_class() == 'TButton' and widget.cget('text') == text:
                widget.invoke()
                self.flush()
                return
            pending.extend(widget.winfo_children())
        self.fail('Button not found: ' + text)

    def test_wardrobe_save_restore_and_reload(self):
        room = self.room
        initial_count = len(room.wardrobe)
        room.tabs.select(room.closet)
        for key, value in dict(name='Acceptance shirt', gender='women', category='top',
                               weather='dry', occasion='casual').items():
            room.fields[key].set(value)
        self.button('Add clothing')
        self.assertEqual(len(room.tree.get_children()), initial_count + 1)
        index = str(len(room.wardrobe) - 1)
        room.tree.selection_set(index)
        self.flush()
        for key, value in room.style_fields.items():
            value.set(key == 'minimal')
        self.button('Update selected styles')
        self.assertEqual(room.wardrobe[-1]['styles'], ['minimal'])
        room.preferred_style.set('Minimal')
        self.button('Recommend')
        room.select(room.wardrobe[-1])
        self.assertTrue(complete(room.outfit))
        self.button('Save this look')
        snapshot = deepcopy(room.history[0])
        self.assertEqual(snapshot['outfit']['top']['name'], 'Acceptance shirt')

        room.tree.selection_set(index)
        self.flush()
        self.button('Remove selected')
        self.assertEqual(len(room.wardrobe), initial_count)
        self.assertNotIn('top', room.outfit)
        self.assertEqual(room.history[0], snapshot)
        room.tabs.select(room.past)
        room.saved.selection_set(0)
        self.button('Wear selected look')
        self.assertEqual(room.outfit, snapshot['outfit'])
        self.assertEqual(room.context(), ('women', 'dry', 'casual', 'minimal'))

        # Recreate all widgets from disk, rather than reusing in-memory lists.
        for child in self.root.winfo_children():
            child.destroy()
        reloaded = DressingRoom(
            self.root,
            model.load_data('wardrobe.json', [], model.valid_clothing),
            model.load_data('outfit_history.json', [], model.valid_history))
        reloaded.saved.selection_set(0)
        self.button('Wear selected look')
        self.assertEqual(reloaded.outfit, snapshot['outfit'])
        self.assertEqual(len(reloaded.wardrobe), initial_count)
        self.dialogs['showerror'].assert_not_called()

    def test_all_plan_combinations_and_artwork(self):
        room = self.room
        for gender in ['Women', 'Men']:
            for weather in ['Dry', 'Rainy']:
                for occasion in model.OCCASIONS:
                    for style in model.STYLE_PREFERENCES:
                        with self.subTest(gender=gender, weather=weather,
                                          occasion=occasion, style=style):
                            for variable, value in [(room.gender, gender), (room.weather, weather),
                                                    (room.occasion, occasion.title()),
                                                    (room.preferred_style, style.title())]:
                                variable.set(value)
                            room.context_changed()
                            room.recommend()
                            self.flush()
                            for item in room.outfit.values():
                                self.assertTrue(model.matches_plan(
                                    item, weather.lower(), occasion, gender.lower(), style))
                            if not complete(room.outfit):
                                self.assertIn('Still needed:', room.status.get())
            for item in room.wardrobe:
                if item['gender'] in [gender.lower(), 'unisex']:
                    room.select(item)
                    self.assertGreater(room.item_photo(item, gender.lower()).width(), 0)
            room.shuffle()
            self.assertTrue(complete(room.outfit))
        self.flush()

    def test_added_clothing_is_revealed_across_filters_and_categories(self):
        room = self.room
        for gender, category in [('men', 'bottom'), ('women', 'dress'), ('unisex', 'shoes')]:
            with self.subTest(gender=gender, category=category):
                room.gender.set('Men' if gender != 'men' else 'Women')
                room.context_changed()
                room.category = 'top'
                room.only_matching.set(True)
                room.occasion.set('Sport')
                room.tabs.select(room.closet)
                name = f'ZZZ new {gender} {category}'
                for key, value in dict(name=name, gender=gender, category=category,
                                       weather='dry', occasion='wedding').items():
                    room.fields[key].set(value)
                self.button('Add clothing')
                self.assertEqual(room.tabs.select(), str(room.studio))
                self.assertEqual(room.category, category)
                self.assertEqual(room.context()[0], 'men' if gender == 'unisex' else gender)
                self.assertFalse(room.only_matching.get())
                self.assertEqual(room.outfit[category]['name'], name)
                first_card = room.gallery.winfo_children()[0]
                labels = [widget.cget('text') for widget in first_card.winfo_children()]
                self.assertIn(name, labels)
                self.assertEqual(float(room.gallery_canvas.yview()[0]), 0.0)
                self.assertTrue(any(room.stage.type(key) == 'image' for key in room.stage.find_all()))
                # The wardrobe action also finds an existing item after navigation.
                room.tabs.select(room.closet)
                room.category = 'top'
                room.only_matching.set(True)
                room.tree.selection_set(str(len(room.wardrobe) - 1))
                self.button('Try on selected')
                self.assertEqual(room.tabs.select(), str(room.studio))
                self.assertEqual(room.outfit[category]['name'], name)

    def test_invalid_input_and_failed_writes_preserve_state(self):
        room = self.room
        original = deepcopy(room.wardrobe)
        room.fields['name'].set('   ')
        self.button('Add clothing')
        self.dialogs['showwarning'].assert_called_once()
        self.assertEqual(room.wardrobe, original)
        room.fields['name'].set('Unsaved shirt')
        with patch.object(model, 'save_data', side_effect=OSError('Test: disk not writable')):
            self.button('Add clothing')
            self.assertEqual(room.wardrobe, original)
            self.button('Save this look')
            self.assertEqual(room.history, [])
        self.assertEqual(self.dialogs['showerror'].call_count, 2)
        room.outfit = {}
        self.button('Save this look')
        self.dialogs['showinfo'].assert_called_once()
        self.assertFalse((model.BASE_DIR / 'outfit_history.json').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
