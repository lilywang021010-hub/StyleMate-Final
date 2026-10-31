"""The illustrated Tkinter dressing room. All artwork lives in assets/pixel."""
import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

import stylemate as model

ART = Path(__file__).resolve().parent / 'assets' / 'pixel'
with (ART / 'catalog.json').open(encoding='utf-8') as catalog_file:
    ART_CATALOG = json.load(catalog_file)
BG = '#f4edf7'
PANEL = '#fffafd'
INK = '#49384f'
MUTED = '#88758e'
ACCENT = '#aa6ba9'
BORDER = '#d9c5df'
STAGE = '#fcf2f7'
CATEGORY_LABELS = {'top': 'Tops', 'bottom': 'Bottoms', 'dress': 'Dresses', 'shoes': 'Shoes'}


def wear_item(outfit, item):
    """A dress replaces separates; separates replace a dress."""
    updated = {key: value.copy() for key, value in outfit.items()}
    if item['category'] == 'dress':
        updated.pop('top', None)
        updated.pop('bottom', None)
    elif item['category'] in ['top', 'bottom']:
        updated.pop('dress', None)
    updated[item['category']] = item.copy()
    return updated


def complete(outfit):
    return set(outfit) in [{'top', 'bottom', 'shoes'}, {'dress', 'shoes'}]


def art_variant(item, gender):
    """Pick a reusable illustration template for each garment style."""
    if isinstance(item.get('art'), int) and 0 <= item['art'] < 6:
        if item['category'] != 'dress' or item['art'] in [3, 5]:
            return item['art']
    name = item['name'].lower()
    category = item['category']
    occasion = item['occasion']
    if category == 'dress':
        return 5 if occasion == 'beach' or 'sundress' in name else 3
    if category == 'shoes':
        if 'sandal' in name:
            return 5
        if 'running' in name or occasion == 'sport':
            return 4
        if 'heel' in name:
            return 3 if occasion in ['wedding', 'party'] else 0
        if 'leather' in name or occasion in ['work', 'formal', 'wedding']:
            return 2
        return 1
    if category == 'bottom':
        if 'skirt' in name:
            return 0
        if 'legging' in name or occasion == 'sport':
            return 4
        if 'short' in name or occasion == 'beach':
            return 5 if gender == 'men' else 1
        if 'jeans' in name:
            return 1 if gender == 'women' else 0
        return 2 if occasion in ['work', 'formal', 'wedding'] else 1
    if occasion == 'sport':
        return 4
    if 'suit' in name and gender == 'men':
        return 3
    if 'linen' in name and gender == 'men':
        return 5
    if any(word in name for word in ['knit', 'sweater']) or occasion == 'date':
        return 0
    if 't-shirt' in name or occasion == 'casual':
        return 1
    if occasion in ['work', 'formal', 'wedding', 'party'] or 'blouse' in name:
        return 2
    return 0


def art_spec(item, gender):
    """Built-in clothes use explicit artwork, including their named colours."""
    known = ART_CATALOG.get(gender, {}).get(item['name'].strip().lower())
    if known:
        return known[0], known[1]
    return 'base', art_variant(item, gender)


class DressingRoom:
    def __init__(self, root, wardrobe, history):
        self.root, self.wardrobe, self.history = root, wardrobe, history
        self.outfit = {}
        self.photos = {}
        self.category = 'top'
        self.revealed_item = None
        self.gender = tk.StringVar(value='Women')
        self.weather = tk.StringVar(value='Dry')
        self.occasion = tk.StringVar(value='Casual')
        self.preferred_style = tk.StringVar(value='Any')
        self.only_matching = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value='Click a clothing card to try it on.')
        self.match_text = tk.StringVar()
        self.last_gender = 'women'
        self.selected_labels = {}
        self.history_entries = []
        root.title('StyleMate — Personal outfit planner')
        root.geometry('1160x820')
        root.minsize(1020, 760)
        root.configure(bg=BG)
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('.', font=('Helvetica', 12), foreground=INK, background=BG)
        style.configure('TNotebook', background=BG, borderwidth=0)
        style.configure('TNotebook.Tab', padding=(20, 9), background='#e8dced')
        style.map('TNotebook.Tab', background=[('selected', PANEL)])
        style.configure('TFrame', background=BG)
        style.configure('TButton', padding=(12, 8), background='#eadbef', bordercolor=BORDER)
        style.configure('Accent.TButton', background=ACCENT, foreground='white', padding=(12, 11))
        style.map('Accent.TButton', background=[('active', '#955b95')])
        style.configure('TCombobox', padding=5, fieldbackground=PANEL, arrowsize=16)
        style.configure('Treeview', background=PANEL, fieldbackground=PANEL, rowheight=29)
        style.configure('Treeview.Heading', background='#eadbef', padding=7)
        header = tk.Frame(root, bg='#e4cfe9', padx=22, pady=14)
        header.pack(fill='x')
        tk.Label(header, text='✧  STYLEMATE', bg='#e4cfe9', fg=INK,
                 font=('Courier', 25, 'bold')).pack(side='left')
        tk.Label(header, text='personal outfit planner', bg='#e4cfe9', fg='#725c7a',
                 font=('Helvetica', 12)).pack(side='left', padx=24)
        tk.Label(header, text='✦  mix · match · save', bg='#e4cfe9', fg='#725c7a',
                 font=('Helvetica', 11)).pack(side='right')
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill='both', expand=True, padx=16, pady=(12, 0))
        self.studio, self.closet, self.past = [ttk.Frame(self.tabs, padding=12) for _ in range(3)]
        for frame, name in [(self.studio, 'Dressing room'), (self.closet, 'My wardrobe'), (self.past, 'Saved looks')]:
            self.tabs.add(frame, text=name)
        tk.Label(root, textvariable=self.status, bg=BG, fg=MUTED, anchor='w',
                 font=('Helvetica', 11), padx=20, pady=10).pack(fill='x')
        self.build_studio()
        self.build_wardrobe()
        self.build_history()
        self.recommend()

    def context(self):
        return (self.gender.get().lower(), self.weather.get().lower(),
                self.occasion.get().lower(), self.preferred_style.get().lower())

    def panel(self, parent):
        return tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)

    def build_studio(self):
        filters = tk.Frame(self.studio, bg=BG)
        filters.pack(fill='x', pady=(0, 12))
        for label, variable, values, width in [
                ('Wardrobe', self.gender, ['Women', 'Men'], 10),
                ('Weather', self.weather, ['Dry', 'Rainy'], 9),
                ('Occasion', self.occasion, [s.title() for s in model.OCCASIONS], 12),
                ('Style', self.preferred_style, [s.title() for s in model.STYLE_PREFERENCES], 10)]:
            tk.Label(filters, text=label, bg=BG, fg=MUTED).pack(side='left', padx=(0, 7))
            combo = ttk.Combobox(filters, textvariable=variable, values=values, state='readonly', width=width)
            combo.pack(side='left', padx=(0, 18))
            combo.bind('<<ComboboxSelected>>', self.context_changed)
        self.body = tk.Frame(self.studio, bg=BG)
        self.body.pack(fill='both', expand=True)
        self.body.grid_columnconfigure(0, weight=1, minsize=340)
        self.body.grid_columnconfigure(1, weight=1, minsize=320)
        self.body.grid_columnconfigure(2, weight=0, minsize=230)
        self.body.grid_rowconfigure(0, weight=1)
        left = self.panel(self.body)
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        title = tk.Frame(left, bg=PANEL, padx=12, pady=12)
        title.pack(fill='x')
        tk.Label(title, text='THE CLOSET', bg=PANEL, fg=INK, font=('Courier', 14, 'bold')).pack(side='left')
        self.count_label = tk.Label(title, bg=PANEL, fg=MUTED, font=('Helvetica', 10))
        self.count_label.pack(side='right')
        cats = tk.Frame(left, bg=PANEL)
        cats.pack(fill='x', padx=8)
        self.category_buttons = {}
        for category, text in CATEGORY_LABELS.items():
            button = tk.Label(cats, text=text, bg=PANEL, fg=MUTED, padx=9, pady=9, cursor='hand2')
            button.pack(side='left', expand=True, fill='x')
            button.bind('<Button-1>', lambda event, key=category: self.change_category(key))
            self.category_buttons[category] = button
        tk.Checkbutton(left, text='Show only pieces matching my plan',
                       variable=self.only_matching, command=self.refresh_gallery,
                       bg=PANEL, fg=MUTED, activebackground=PANEL, font=('Helvetica', 10)).pack(anchor='w', padx=10, pady=7)
        gallery_host = tk.Frame(left, bg=PANEL)
        gallery_host.pack(fill='both', expand=True, padx=6, pady=(0, 8))
        self.gallery_canvas = tk.Canvas(gallery_host, bg=PANEL, highlightthickness=0, width=340)
        scroll = ttk.Scrollbar(gallery_host, command=self.gallery_canvas.yview)
        scroll.pack(side='right', fill='y')
        self.gallery_canvas.pack(side='left', fill='both', expand=True)
        self.gallery_canvas.configure(yscrollcommand=scroll.set)
        self.gallery = tk.Frame(self.gallery_canvas, bg=PANEL)
        self.gallery_id = self.gallery_canvas.create_window(0, 0, anchor='nw', window=self.gallery)
        self.gallery.bind('<Configure>', lambda event: self.gallery_canvas.configure(scrollregion=self.gallery_canvas.bbox('all')))
        self.gallery_canvas.bind('<Configure>', lambda event: self.gallery_canvas.itemconfigure(self.gallery_id, width=event.width))
        for col in [0, 1]:
            self.gallery.grid_columnconfigure(col, weight=1)
        middle = self.panel(self.body)
        middle.grid(row=0, column=1, sticky='nsew', padx=(0, 10))
        tk.Label(middle, text='✧  FITTING ROOM  ✧', bg=PANEL, fg=MUTED,
                 font=('Courier', 12, 'bold'), pady=13).pack(fill='x')
        self.stage = tk.Canvas(middle, bg=STAGE, highlightthickness=0, width=320, height=530)
        self.stage.pack(fill='both', expand=True, padx=8)
        self.stage.bind('<Configure>', lambda event: self.draw_doll())
        tk.Label(middle, text='Click a piece in the closet to change your look.',
                 bg=PANEL, fg=MUTED, wraplength=300, font=('Helvetica', 10), pady=10).pack(fill='x')
        right = self.panel(self.body)
        right.grid(row=0, column=2, sticky='nsew')
        tk.Label(right, text='YOUR LOOK', bg=PANEL, fg=INK,
                 font=('Courier', 14, 'bold'), pady=16).pack(anchor='w', padx=16)
        for category in ['top', 'bottom', 'dress', 'shoes']:
            tk.Label(right, text=CATEGORY_LABELS[category].upper(), bg=PANEL, fg=ACCENT,
                     font=('Helvetica', 9, 'bold')).pack(anchor='w', padx=16, pady=(9, 3))
            label = tk.Label(right, bg=PANEL, fg=INK, wraplength=190, justify='left',
                             anchor='w', font=('Helvetica', 12))
            label.pack(fill='x', padx=16)
            self.selected_labels[category] = label
        tk.Label(right, textvariable=self.match_text, bg='#f0e7f3', fg='#725576',
                 wraplength=185, justify='left', padx=10, pady=11, font=('Helvetica', 11)).pack(fill='x', padx=12, pady=18)
        for text, command, style in [('Recommend', self.recommend, 'Accent.TButton'),
                                      ('Shuffle look', self.shuffle, 'TButton'),
                                      ('Save this look', self.save, 'TButton')]:
            ttk.Button(right, text=text, command=command, style=style).pack(fill='x', padx=12, pady=(0, 9))
        tk.Label(right, text='Built-in pieces use matched artwork. New custom pieces use a style preview.',
                 bg=PANEL, fg=MUTED, font=('Helvetica', 9), wraplength=190,
                 justify='left').pack(side='bottom', padx=15, pady=14)

    def photo(self, gender, category, index, thumbnail=False, collection='base'):
        if category == 'dress':
            gender = 'women'
        filename = f'{gender}_{category}_{index}' + ('_thumb' if thumbnail else '') + '.gif'
        path = ART / filename if collection == 'base' else ART / collection / filename
        key = str(path)
        if key not in self.photos:
            self.photos[key] = tk.PhotoImage(master=self.root, file=key)
        return self.photos[key]

    def item_photo(self, item, gender, thumbnail=False):
        collection, index = art_spec(item, gender)
        return self.photo(gender, item['category'], index, thumbnail, collection)

    def change_category(self, category):
        self.category = category
        self.refresh_gallery()
        self.gallery_canvas.yview_moveto(0)

    def context_changed(self, event=None):
        gender, _, _, _ = self.context()
        if gender != self.last_gender:
            self.last_gender = gender
            self.outfit = {}
            self.recommend()
        else:
            self.refresh()

    def refresh_gallery(self):
        for child in self.gallery.winfo_children():
            child.destroy()
        gender, weather, occasion, style = self.context()
        items = [item for item in self.wardrobe if item['category'] == self.category
                 and item['gender'] in [gender, 'unisex']]
        if self.only_matching.get():
            items = [item for item in items if model.matches_plan(item, weather, occasion, gender, style)]
        items.sort(key=lambda item: (item != self.revealed_item,
                                    not model.matches_plan(item, weather, occasion, gender, style), item['name']))
        self.count_label.config(text=f'{len(items)} pieces')
        for key, button in self.category_buttons.items():
            button.config(bg='#e9d6ee' if key == self.category else PANEL,
                          fg=INK if key == self.category else MUTED)
        if not items:
            tk.Label(self.gallery, text='No pieces here yet.\nAdd one in My wardrobe or change the filter.',
                     bg=PANEL, fg=MUTED, wraplength=260, pady=28).grid(columnspan=2)
        for index, item in enumerate(items):
            selected = self.outfit.get(item['category']) == item
            card = tk.Frame(self.gallery, bg=STAGE, cursor='hand2',
                            highlightbackground=ACCENT if selected else BORDER,
                            highlightthickness=3 if selected else 1, width=158, height=188)
            card.grid(row=index // 2, column=index % 2, padx=5, pady=5, sticky='nsew')
            card.grid_propagate(False)
            card.pack_propagate(False)
            image = self.item_photo(item, gender, thumbnail=True)
            picture = tk.Label(card, image=image, bg=STAGE, height=106)
            picture.pack(fill='x', pady=(3, 0))
            name = tk.Label(card, text=item['name'], bg=STAGE, fg=INK, wraplength=144,
                            font=('Helvetica', 10, 'bold'))
            name.pack(fill='x')
            tag = tk.Label(card, text=item['occasion'].title() + '\n' + ' / '.join(item['styles']),
                           wraplength=144, bg=STAGE, fg=MUTED, font=('Helvetica', 9))
            tag.pack(side='bottom', pady=4)
            for widget in [card, picture, name, tag]:
                widget.bind('<Button-1>', lambda event, clothing=item: self.select(clothing))

    def select(self, item):
        self.outfit = wear_item(self.outfit, item)
        self.status.set(f'Trying on: {item["name"]}.')
        self.refresh()

    def draw_doll(self):
        self.stage.delete('all')
        gender, _, _, _ = self.context()
        width = max(self.stage.winfo_width(), 300)
        x = (width - 248) // 2
        y = max(8, (self.stage.winfo_height() - 506) // 2)
        self.stage.create_image(x, y, image=self.photo(gender, 'head', 0), anchor='nw')
        y += 136 if gender == 'women' else 124
        if 'dress' in self.outfit:
            dress = self.item_photo(self.outfit['dress'], gender)
            self.stage.create_image(x + (248 - dress.width()) // 2, y, image=dress, anchor='nw')
            # Keep the gown's outer hem while changing the central shoe area.
            if 'shoes' in self.outfit:
                source = self.item_photo(self.outfit['shoes'], gender)
                collection, index = art_spec(self.outfit['shoes'], gender)
                key = f'shoe-inset-{gender}-{collection}-{index}'
                if key not in self.photos:
                    inset = tk.PhotoImage(master=self.root, width=132, height=48)
                    inset.tk.call(inset, 'copy', source, '-from', 58, 0, 190, 48, '-to', 0, 0)
                    self.photos[key] = inset
                self.stage.create_image(x + 58, y + 322, image=self.photos[key], anchor='nw')
        else:
            heights = [88, 234, 48] if gender == 'women' else [144, 190, 48]
            for category, height in zip(['top', 'bottom', 'shoes'], heights):
                item = self.outfit.get(category)
                if item:
                    self.stage.create_image(x, y, image=self.item_photo(item, gender), anchor='nw')
                else:
                    self.stage.create_rectangle(x + 30, y + 4, x + 218, y + height - 4,
                                                outline=BORDER, dash=(3, 3))
                    self.stage.create_text(x + 124, y + height / 2, text=f'Choose {CATEGORY_LABELS[category].lower()}',
                                           fill=MUTED, font=('Helvetica', 11))
                y += height

    def refresh(self):
        self.refresh_gallery()
        self.draw_doll()
        gender, weather, occasion, style = self.context()
        for category, label in self.selected_labels.items():
            label.config(text=self.outfit.get(category, {}).get('name', '—'))
        if not complete(self.outfit):
            self.match_text.set('Choose a top + bottom + shoes, or a dress + shoes.')
        else:
            mismatch = sum(not model.matches_plan(item, weather, occasion, gender, style)
                           for item in self.outfit.values())
            self.match_text.set(f'✓ Ready for {occasion}.\nStyle: {style.title()}. All pieces match.' if not mismatch else
                                f'Free styling · {mismatch} piece(s) differ from your weather, occasion or style.')

    def recommend(self):
        gender, weather, occasion, style = self.context()
        outfit, missing = model.choose_outfit(self.wardrobe, weather, occasion, gender, style)
        self.outfit = outfit
        if missing:
            self.status.set('Still needed: ' + ', '.join(missing) + '. Try Style: Any, another plan, or add suitable clothing.')
        else:
            self.status.set('A look for your plan. Click any card to change a piece.')
        self.refresh()

    def shuffle(self):
        gender, _, _, _ = self.context()
        self.outfit = model.shuffle_outfit(self.wardrobe, gender)
        self.status.set('A surprise mix. Recommend will match weather, occasion and style.'
                        if complete(self.outfit) else
                        'Your wardrobe needs more pieces for a complete look. Add clothing in My wardrobe.')
        self.refresh()

    def persist(self, filename, data):
        try:
            model.save_data(filename, data)
            return True
        except OSError as error:
            messagebox.showerror('Could not save', str(error), parent=self.root)
            return False

    def save(self):
        if not complete(self.outfit):
            messagebox.showinfo('Finish your look', 'Choose shoes and either a dress or a top and bottom.', parent=self.root)
            return
        gender, weather, occasion, style = self.context()
        updated = self.history + [model.history_entry(self.outfit, weather, occasion, gender, style)]
        if self.persist('outfit_history.json', updated):
            self.history[:] = updated
            self.refresh_history()
            self.status.set('Look saved. You can wear it again from Saved looks.')

    def build_wardrobe(self):
        tk.Label(self.closet, text='Your collection', bg=BG, fg=INK,
                 font=('Helvetica', 20, 'bold')).pack(anchor='w', pady=(0, 12))
        host = ttk.Frame(self.closet)
        host.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(host, columns=('name', 'gender', 'category', 'weather', 'occasion', 'styles'), show='headings')
        for column in self.tree['columns']:
            self.tree.heading(column, text=column.title())
            self.tree.column(column, width=220 if column in ['name', 'styles'] else 100)
        bar = ttk.Scrollbar(host, command=self.tree.yview)
        bar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=bar.set)
        self.tree.pack(fill='both', expand=True)
        form = ttk.Frame(self.closet)
        form.pack(fill='x', pady=18)
        self.fields = {}
        for i, (key, values) in enumerate([('name', None), ('gender', model.GENDERS),
                                          ('category', model.CATEGORIES), ('weather', model.WEATHER),
                                          ('occasion', model.OCCASIONS)]):
            tk.Label(form, text=key.title(), bg=BG, fg=MUTED).grid(row=0, column=i, sticky='w', padx=5)
            variable = tk.StringVar(value=values[0] if values else '')
            self.fields[key] = variable
            widget = (ttk.Combobox(form, textvariable=variable, values=values, state='readonly', width=13)
                      if values else ttk.Entry(form, textvariable=variable, width=25))
            widget.grid(row=1, column=i, padx=5, pady=5)
        tags = ttk.Frame(self.closet)
        tags.pack(fill='x', pady=(0, 12))
        tk.Label(tags, text='Styles (one or more):', bg=BG, fg=MUTED).pack(side='left', padx=(0, 10))
        self.style_fields = {}
        for tag in model.STYLES:
            variable = tk.BooleanVar(value=tag == 'casual')
            self.style_fields[tag] = variable
            ttk.Checkbutton(tags, text=tag.title(), variable=variable).pack(side='left', padx=7)
        self.tree.bind('<<TreeviewSelect>>', self.load_selected_styles)
        actions = ttk.Frame(self.closet)
        actions.pack(fill='x')
        ttk.Button(actions, text='Add clothing', command=self.add, style='Accent.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(actions, text='Remove selected', command=self.remove).pack(side='left')
        ttk.Button(actions, text='Update selected styles', command=self.update_styles).pack(side='left', padx=10)
        ttk.Button(actions, text='Try on selected', command=self.try_selected).pack(side='left')
        self.refresh_wardrobe()

    def show_clothing(self, item):
        """Reveal and wear a wardrobe item even if the current gallery hides it."""
        if item['gender'] != 'unisex' and item['gender'] != self.context()[0]:
            self.gender.set(item['gender'].title())
            self.last_gender = item['gender']
            self.outfit = {}
        self.category = item['category']
        self.only_matching.set(False)
        self.revealed_item = item.copy()
        self.outfit = wear_item(self.outfit, item)
        self.tabs.select(self.studio)
        self.refresh()
        self.gallery_canvas.yview_moveto(0)

    def try_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo('Select clothing', 'Select an item in the table first.', parent=self.root)
            return
        item = self.wardrobe[int(selection[0])]
        self.show_clothing(item)
        self.status.set(f'Trying on: {item["name"]}. Showing all pieces in this category.')

    def load_selected_styles(self, event=None):
        selection = self.tree.selection()
        if selection:
            styles = self.wardrobe[int(selection[0])]['styles']
            for key, variable in self.style_fields.items():
                variable.set(key in styles)

    def update_styles(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo('Select clothing', 'Select an item in the table first.', parent=self.root)
            return
        styles = [key for key, value in self.style_fields.items() if value.get()]
        if not styles:
            messagebox.showwarning('Choose a style', 'Select at least one style.', parent=self.root)
            return
        index = int(selection[0])
        old_item = self.wardrobe[index]
        updated = self.wardrobe.copy()
        updated[index] = dict(old_item, styles=styles)
        if self.persist('wardrobe.json', updated):
            self.wardrobe[:] = updated
            if self.outfit.get(old_item['category']) == old_item:
                self.outfit[old_item['category']] = updated[index].copy()
            self.refresh_wardrobe()
            self.refresh()
            self.status.set('Style tags updated and saved.')

    def refresh_wardrobe(self):
        self.tree.delete(*self.tree.get_children())
        for index, item in enumerate(self.wardrobe):
            self.tree.insert('', 'end', iid=str(index), values=[', '.join(item[key]) if key == 'styles' else item[key] for key in self.tree['columns']])

    def add(self):
        item = {key: value.get().strip() for key, value in self.fields.items()}
        item['styles'] = [key for key, value in self.style_fields.items() if value.get()]
        if not model.valid_clothing(item):
            messagebox.showwarning('Check clothing', 'Enter a name, valid clothing options and at least one style.', parent=self.root)
            return
        updated = self.wardrobe + [item]
        if self.persist('wardrobe.json', updated):
            self.wardrobe[:] = updated
            self.fields['name'].set('')
            self.refresh_wardrobe()
            self.show_clothing(item)
            self.status.set(f'Added and saved: {item["name"]}. Now trying it on; showing all pieces in this category.')

    def remove(self):
        selection = self.tree.selection()
        if not selection:
            return
        index = int(selection[0])
        item = self.wardrobe[index]
        if not messagebox.askyesno('Remove clothing', f'Remove {item["name"]}?', parent=self.root):
            return
        updated = self.wardrobe.copy()
        updated.pop(index)
        if self.persist('wardrobe.json', updated):
            self.wardrobe[:] = updated
            if self.outfit.get(item['category']) == item:
                self.outfit.pop(item['category'])
            self.refresh_wardrobe()
            self.refresh()
            self.status.set('Clothing removed. Previously saved looks are still available.')

    def build_history(self):
        tk.Label(self.past, text='Looks you loved', bg=BG, fg=INK,
                 font=('Helvetica', 20, 'bold')).pack(anchor='w', pady=(0, 12))
        self.saved = tk.Listbox(self.past, bg=PANEL, fg=INK, selectbackground='#dfc8e8',
                               selectforeground=INK, highlightbackground=BORDER,
                               font=('Helvetica', 12), activestyle='none')
        self.saved.pack(fill='both', expand=True, pady=(0, 12))
        ttk.Button(self.past, text='Wear selected look', command=self.load_look, style='Accent.TButton').pack(anchor='w')
        self.refresh_history()

    def refresh_history(self):
        self.saved.delete(0, 'end')
        self.history_entries = list(reversed(self.history))
        if not self.history_entries:
            self.saved.insert('end', 'No saved looks yet. Style an outfit and click Save this look.')
        for entry in self.history_entries:
            clothes = ' + '.join(item['name'] for item in entry['outfit'].values())
            self.saved.insert('end', f'{entry["date"]}   ·   {entry["gender"].title()} / {entry["occasion"].title()} / {entry["style"].title()}   ·   {clothes}')

    def load_look(self):
        selection = self.saved.curselection()
        if not selection or not self.history_entries:
            return
        entry = self.history_entries[selection[0]]
        self.gender.set(entry['gender'].title() if entry['gender'] != 'unisex' else 'Women')
        self.last_gender = self.gender.get().lower()
        self.weather.set(entry['weather'].title())
        self.occasion.set(entry['occasion'].title())
        self.preferred_style.set(entry['style'].title())
        self.outfit = {key: item.copy() for key, item in entry['outfit'].items()}
        self.tabs.select(self.studio)
        self.refresh()
        self.status.set('Saved look restored. Keep styling or save a new version.')


def launch(wardrobe, history):
    root = tk.Tk()
    try:
        DressingRoom(root, wardrobe, history)
    except (OSError, tk.TclError) as error:
        messagebox.showerror('StyleMate could not start', f'Check that the assets folder is beside stylemate.py.\n\n{error}', parent=root)
        root.destroy()
        return
    root.mainloop()
