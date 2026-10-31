"""Run the real command-line program in a disposable project copy."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class TerminalPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name) / 'project'
        self.folder.mkdir()
        source = Path(__file__).resolve().parents[1]
        shutil.copy2(source / 'stylemate.py', self.folder / 'stylemate.py')

    def run_program(self, answers):
        # Launch from outside the project to verify storage is script-relative.
        result = subprocess.run(
            [sys.executable, str(self.folder / 'stylemate.py'), '--terminal'],
            input=answers, capture_output=True, text=True, cwd=self.temp.name,
            timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        return result.stdout

    def test_add_recommend_save_restart_and_remove(self):
        output = self.run_program('\n'.join([
            '2', 'Demo test shirt', 'women', 'top', 'any', 'casual', 'minimal',
            '4', 'women', 'dry', 'casual', 'minimal', 'y', '0', '']))
        self.assertIn('Added and saved.', output)
        self.assertIn('Outfit saved.', output)
        wardrobe = json.loads((self.folder / 'wardrobe.json').read_text())
        saved = json.loads((self.folder / 'outfit_history.json').read_text())
        self.assertEqual(saved[0]['style'], 'minimal')
        self.assertEqual(set(saved[0]['outfit']), {'top', 'bottom', 'shoes'})
        output = self.run_program('1\n5\n0\n')
        self.assertIn('Demo test shirt', output)
        self.assertIn(saved[0]['date'], output)
        number = next(i for i, item in enumerate(wardrobe, 1)
                      if item['name'] == 'Demo test shirt')
        self.run_program(f'3\n{number}\n0\n')
        remaining = json.loads((self.folder / 'wardrobe.json').read_text())
        self.assertFalse(any(item['name'] == 'Demo test shirt' for item in remaining))
        self.assertEqual(json.loads((self.folder / 'outfit_history.json').read_text()), saved)
        self.assertFalse((Path(self.temp.name) / 'wardrobe.json').exists())

    def test_invalid_file_is_reported_and_preserved(self):
        path = self.folder / 'wardrobe.json'
        path.write_text('{invalid json', encoding='utf-8')
        output = self.run_program('')
        self.assertIn('Cannot read wardrobe.json', output)
        self.assertEqual(path.read_text(), '{invalid json')


if __name__ == '__main__':
    unittest.main()
