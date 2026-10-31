"""Build a local source-and-assets archive; does not upload or submit anything."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def build():
    destination = ROOT / 'dist'
    destination.mkdir(exist_ok=True)
    archive = destination / 'StyleMate-submission.zip'
    files = [ROOT / name for name in [
        'stylemate.py', 'dressup_ui.py', 'wardrobe.json', 'README.txt', 'README.md',
        'Start_StyleMate.command', 'USER_GUIDE.md']]
    for folder in ['assets', 'tests', 'tools']:
        files.extend(path for path in (ROOT / folder).rglob('*')
                     if path.is_file() and '__pycache__' not in path.parts
                     and path.name != '.DS_Store' and path.suffix != '.pyc')
    # Personal outfit history and private presentation/email drafts are not included.
    with ZipFile(archive, 'w', ZIP_DEFLATED) as output:
        for path in sorted(files):
            output.write(path, Path('StyleMate') / path.relative_to(ROOT))
    print(f'Created {archive} ({len(files)} files)')


if __name__ == '__main__':
    build()
