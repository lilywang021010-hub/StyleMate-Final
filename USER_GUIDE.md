# StyleMate - User Guide

StyleMate is a Python desktop application for managing a digital wardrobe,
recommending outfits and trying clothing combinations in a visual dressing room.

## 1. Run the application

1. Extract the complete project folder. Keep its files and subfolders together.
2. Use Python 3 with working Tkinter and Tcl/Tk 8.6 or newer.
3. Open a terminal in the extracted folder and run:

   - macOS or Linux: `python3 stylemate.py`
   - Windows: `py stylemate.py`

To check Tkinter, run `python3 -m tkinter` (Windows: `py -m tkinter`). A small
test window should appear. If Tkinter is unavailable, use a Python installation
that includes Tkinter/Tcl/Tk support.

The graphical application must run locally, outside Ed's environment. No pip
packages, internet connection, account or API key are needed to run StyleMate.
Anaconda is not required. `Start_StyleMate.command` is an optional macOS launcher.

A text-only alternative is available with `python3 stylemate.py --terminal`
(Windows: `py stylemate.py --terminal`). It supports wardrobe management,
recommendations, saving and history, but does not display the dressing room.

## 2. Recommend an outfit

In **Dressing room**, select:

| Control | Options or purpose |
| --- | --- |
| Wardrobe | Women or Men; unisex clothing is available in either wardrobe. |
| Weather | Dry or Rainy. |
| Occasion | Casual, University, Work, Formal, Date, Party, Sport, Wedding or Beach. |
| Style | Any, Casual, Minimal, Cute, Sporty or Elegant. |

Click **Recommend**. The program selects clothing that matches the chosen
conditions. If a complete outfit is unavailable, it shows the matching pieces
and explains which categories are missing. **Any** leaves style unrestricted.

For a simple demonstration, choose **Women / Dry / University / Any** and click
**Recommend**. Results depend on the items currently in the wardrobe.

## 3. Try and save combinations

1. Select **Tops**, **Bottoms**, **Dresses** or **Shoes** on the left.
2. Click a clothing card to wear it on the illustrated character. A dress
   replaces the selected top and bottom; choosing a top or bottom removes a dress.
3. Use **Shuffle look** to mix clothing freely within the selected wardrobe.
   Shuffle does not restrict choices by weather, occasion or style.
4. Click **Save this look** to save a complete outfit: a top, bottom and shoes,
   or a dress and shoes. Complete manual combinations can be saved even if they
   do not match the recommendation conditions.
5. Open **Saved looks**, select a record and click **Wear selected look** to
   restore it.

Select **Show only pieces matching my plan** to filter the visible clothing cards.

## 4. Manage the wardrobe

Open **My wardrobe**:

- **Add clothing:** Enter a name, gender, category, weather and occasion, select
  at least one style, then click **Add clothing**.
- After a successful addition, the dressing room opens and tries on the new
  item. Its category and wardrobe are selected, its card appears first, and the
  matching-only filter is cleared so the item is visible. Unisex items keep the
  current wardrobe selection.
- **Try on selected:** Select an existing wardrobe row and click this button to
  find and wear that item in the dressing room.
- **Update selected styles:** Select an item, change the style selections and
  click this button to save its style tags.
- **Remove selected:** Select an item, click this button and confirm removal.
  Previously saved outfits retain their snapshots.

A clothing item's weather can be **any**, making it suitable for both Dry and
Rainy plans. An item can have multiple style tags.

## 5. Saved data and artwork

- `wardrobe.json` stores the clothing collection.
- `outfit_history.json` is created when an outfit is first saved.
- These files are stored beside the program and loaded when it starts again.
  The project folder must be writable. Use a copy of the folder for experiments
  if the original data needs to be preserved.
- Keep the entire `assets/` folder with the program. Built-in clothing has
  matched illustrations. Newly added custom clothing uses an existing preview
  template; adding a name does not generate a new image or import a photograph.

Weather is selected manually rather than obtained from a live weather service.
Recommendations use clothing tags and random selection, so repeated requests
may produce the same outfit. No machine-learning service runs in the application.

## 6. Short demonstration

1. Briefly introduce the purpose and main features using the Padlet post.
2. Select a plan and click **Recommend**.
3. Click another clothing card to demonstrate manual outfit changes.
4. Save the outfit and restore it from **Saved looks**.
5. Add an item in **My wardrobe** and show it appearing in the dressing room.

Rehearse the sequence within the three-minute presentation limit. Saving and
reopening the application can also be checked before the demonstration to
confirm that wardrobe and outfit history persist.

## 7. Code and checks

- `stylemate.py`: data validation, outfit matching, file I/O and terminal mode.
- `dressup_ui.py`: Tkinter interface, clothing cards and character previews.
- `tests/`: automated recommendation and data tests.
- `tools/`: development utilities and additional checks.

Run the automated tests from the project folder:

```sh
python3 -m unittest discover -s tests -v
```

On Windows, replace `python3` with `py`. Optional GUI integration checks use
`python3 tools/check_gui.py` and require a graphical session. Artwork export and
artwork checks require Pillow only for development; exported images are already
included for normal application use.
