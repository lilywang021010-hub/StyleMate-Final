STYLEMATE - PERSONAL OUTFIT PLANNER
Main entry point: stylemate.py

RUN LOCALLY (GUI)
Extract the whole project folder first. In a terminal, change into that folder.
macOS / Linux: python3 stylemate.py
Windows:       py stylemate.py

Requirements: Python 3 with working tkinter/Tcl/Tk support (Tk 8.6 or newer).
Check Tk support with: python3 -m tkinter (Windows: py -m tkinter).
Some Python distributions do not include Tk; use a Python installation that
supports Tk if the check fails. The GUI cannot run inside Ed's environment.
Please assess the graphical fitting room by running it on a local computer.

On the author's Mac only, Start_StyleMate.command uses the existing Anaconda
Python installation when available. Anaconda is NOT a project requirement.

TEXT-ONLY ALTERNATIVE
python3 stylemate.py --terminal
Windows: py stylemate.py --terminal
This supports wardrobe management, recommendations, saving and history.
It does not display the graphical fitting room.

FILES TO KEEP TOGETHER
stylemate.py         Main program, data validation, recommendation, persistence.
dressup_ui.py        Tkinter interface and garment selection.
wardrobe.json       Starter collection / saved wardrobe.
assets/             Image catalogue and all illustration files.
outfit_history.json Created when the first outfit is saved.

Storage is local JSON in the program folder, regardless of the terminal's
working directory. The extracted folder must be writable. There are no accounts,
network services, API keys or internet requirements for running the program.
Use a copy of the folder if you want to experiment without changing your data.

DEPENDENCY DISCLOSURE
The application uses the Python standard library, including tkinter for its GUI.
No pip packages are required to run the application. Tcl/Tk must be available.
Development-only artwork export and colour checks in tools/ use Pillow. These
are not needed to launch the application; exported GIF assets are included.
There is no audio/video processing or networking in the application.

QUICK DEMO
1. Choose Women / Dry / Casual / Minimal and click Recommend.
2. Click a clothing card to change a garment.
3. Save this look. In Saved looks, select it and click Wear selected look.
4. In My wardrobe, add clothing or edit an existing item's style tags.
5. Restart the program to verify that saved data remains available.

SCOPE
Weather is manually selected as dry/rainy, not fetched from a weather service.
Recommendations filter clothing tags, then randomly choose matching pieces.
A complete outfit is top + bottom + shoes, or dress + shoes.
Built-in garments use catalogue illustrations; custom garments use a template.
No images are generated while the application is running.

CHECKS
Course advanced topics: Week 9 File Input/Output and Week 10 Testing.
File I/O is implemented in load_data/save_data. Automated checks in tests/ cover
filtering, incomplete outfits, snapshots, legacy data and persistence on restart.
Classes and objects are also used, but are classified as Essential in the course.

python3 -m unittest discover -s tests -v
These checks do not require opening a window, but importing GUI helpers requires
the tkinter module. Artwork checks additionally require Pillow:
python3 tools/check_artwork.py

Optional local Tk integration checks: python3 tools/check_gui.py
On the author's Mac: /opt/anaconda3/bin/pythonw tools/check_gui.py
These four additional tests use real hidden Tk widgets and temporary JSON
files. They cover wardrobe changes, history restoration, 216 plan combinations,
and failed saves. They mock dialogs and do not test physical mouse input or
visual layout. A graphical session and Tk 8.6+ are required.

Adding clothing opens the fitting room and tries on the new item. Its category
and wardrobe are selected, matching-only filtering is cleared, and its card is
shown first. Unisex clothing keeps the current wardrobe. To find an existing
item, select its row in My wardrobe and click Try on selected. Custom items still
use illustration templates; their names do not generate new pictures.

DEVELOPMENT ASSISTANCE AND ASSETS
AI tools were used during development to assist with implementation,
debugging, testing and documentation. Pixel artwork was generated with OpenAI image generation;
prompts are included under assets/pixel/. Pillow utilities exported the assets.
This describes assistance actually used, not a statement of course permission.
The student should check the course's AI-use rules and make any required
acknowledgment. Presentation and Padlet drafts are provided separately.
