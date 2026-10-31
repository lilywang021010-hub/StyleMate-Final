# StyleMate — Personal Outfit Planner

A Python/Tkinter wardrobe planner with an illustrated dressing room.

For step-by-step instructions and a demonstration walkthrough, see [User Guide](USER_GUIDE.md).

## Start

Extract the complete project folder, open a terminal in that folder, and run:

```sh
python3 stylemate.py
```

On Windows, use `py stylemate.py`. Python 3 with working Tkinter and Tk 8.6 or newer is required. Keep `stylemate.py`, `dressup_ui.py`, `wardrobe.json`, and the entire `assets` folder together. No pip packages are required to run the program. The GUI must run on a local computer, outside Ed's environment. The terminal version remains available with `python3 stylemate.py --terminal` (Windows: `py stylemate.py --terminal`).

`Start_StyleMate.command` is an optional macOS launcher. It uses the author's existing Anaconda installation when available and otherwise tries `python3`. Anaconda is not a project requirement. See `README.txt` for environment checks and dependency details.

## Dressing room

Choose Women or Men, weather, occasion and a preferred style: Casual, Minimal, Cute, Sporty or Elegant. Any leaves style unrestricted. Click Tops, Bottoms, Dresses or Shoes to browse illustrated cards, then click a card to wear it. A dress replaces the selected top and bottom. Selecting a top or bottom removes a dress. Recommend builds an outfit matching all selected conditions and reports missing categories when a complete match is unavailable. Shuffle look mixes pieces freely and tells you when they do not match the selected conditions. Save this look requires shoes plus either a dress or a top and bottom. Saved looks retain the selected style and clothing tags and can be worn again.

My wardrobe adds and removes clothing. Each item has one or more style tags. To edit tags, select a wardrobe row, tick the desired styles and click Update selected styles. The collection includes casual, university, work, formal, date, party, sport, wedding and beach examples. Older records receive starter style tags when loaded; records without a gender remain unisex, and older saved looks use Any for their style preference. Clothing and history JSON files are saved beside the program after changes, independently of the terminal's current directory.

For example, choose Women, Dry, Casual and Minimal, then click Recommend. Switch Style to Any to allow more pieces, or use the cards to mix an outfit manually.

## Artwork and scope

Original fashion-doll artwork was generated with the built-in imagegen tool. `assets/pixel/character-atlas.png` contains six women's and six men's illustrated outfits. `assets/pixel/PROMPTS.json` records the prompt set, including the final pixel-art edit. The artwork uses a light pink background. A second atlas in `assets/pixel/variants/` adds red T-shirts, pink knitwear, black jeans, navy trousers, a red party dress, an ivory wedding gown and other distinct garments. `assets/pixel/catalog.json` explicitly maps the 57 built-in clothing records to their matching illustrations. Cards and the dressed character use the same mapping. Identical garments listed for different occasions can share artwork. New custom clothing without a catalogue entry still uses the closest style preview. The variant prompt is saved in `assets/pixel/variants/PROMPT.txt`.

`tools/prepare_sprites.py` is a development-only atlas export utility. It slices and sizes the generated art into GIF regions and card thumbnails. GIF is used for Tk compatibility; Pillow is only needed to regenerate assets, not to run StyleMate.

## Files and course concepts

- `stylemate.py`: clothing data, matching, validation, JSON saving/loading, terminal mode.
- `dressup_ui.py`: Tkinter windows, card selection, sprite display, saved-look controls.
- `wardrobe.json`: saved collection.
- `outfit_history.json`: created when a look is first saved.

Concepts include functions, classes, conditionals, loops, lists, dictionaries, random selection, file I/O, exception handling and GUI event callbacks. File I/O and exception handling are separate topics. Weather currently means dry/rainy, not temperature.

Artwork regression checks: run `tools/check_artwork.py` with a development Python that has Pillow. It checks catalogue coverage, asset files, distinct garment pairs and actual red/white T-shirt colours.

Recommendation and data compatibility checks: run `python3 -m unittest discover -s tests -v`. These cover style filtering, missing pieces, weather/occasion/gender constraints, saved snapshots, legacy data migration and style validation.

Optional local GUI integration checks: `python3 tools/check_gui.py` (on this Mac, `/opt/anaconda3/bin/pythonw tools/check_gui.py`). Four checks use real hidden Tk widgets and temporary JSON files to exercise registered button commands, wardrobe changes, saved-look restoration, 216 plan combinations and failed saves. Dialog responses are mocked. These checks require a graphical session and do not replace physical mouse/keyboard or visual acceptance testing.

Adding clothing now opens the dressing room, selects the relevant wardrobe and category, clears matching-only filtering and shows the new card first while trying it on. Unisex items keep the current wardrobe. Use Try on selected in My wardrobe to reveal an existing item. Custom clothing uses illustration templates.
