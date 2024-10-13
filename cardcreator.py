import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox, Label
from PIL import Image, ImageDraw, ImageFont, ImageTk
import webbrowser
import traceback

class CardCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Card Creator v5")
        self.root.resizable(True, True)

        # Paths for fonts and graphics
        self.paths = {
            'font_a': None,
            'font_b': None,
            'background_image': None,
            'card_art': None
        }

        # Create UI Elements
        self.create_widgets()

    def create_widgets(self):
        outer_frame = tk.Frame(self.root, padx=10, pady=10)
        outer_frame.pack(expand=True, fill='both')

        # Load Graphics and Fonts
        self.load_buttons(outer_frame)
        self.create_text_entries(outer_frame)
        self.create_action_buttons(outer_frame)

        # Preview panel
        self.preview_panel = tk.Label(outer_frame)
        self.preview_panel.grid(row=0, column=3, rowspan=15, padx=5, pady=10, sticky='n')

        # Created by label and donation link
        tk.Label(outer_frame, text="© 2024 Created by Casey Fallon", font=("Helvetica", 8)).grid(row=20, column=2, sticky='e', padx=5, pady=2)
        buy_me_beer_label = tk.Label(outer_frame, text="Buy me a beer! (venmo)", font=("Helvetica", 8), fg="blue", cursor="hand2")
        buy_me_beer_label.grid(row=21, column=2, sticky='e', padx=5, pady=2)
        buy_me_beer_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://venmo.com/code?user_id=2062052663230464267&created=1728767024"))

    def load_buttons(self, parent):
        load_buttons = [
            ("Load Card Template", 'background_image', 0),
            ("Load Card Art", 'card_art', 1),
            ("Load Font A", 'font_a', 2, "Bold font for item details"),
            ("Load Font B", 'font_b', 3, "Regular font for item description")
        ]

        for text, layer_type, row, *tooltip in load_buttons:
            self.create_load_button(parent, text, layer_type, row, tooltip_text=tooltip[0] if tooltip else None)

    def create_load_button(self, parent, text, layer_type, row, tooltip_text=None):
        button = tk.Button(parent, text=text, command=lambda: self.load_file(layer_type))
        button.grid(row=row, column=0, pady=5, padx=10, sticky='w')
        label = Label(parent, text="Not loaded")
        label.grid(row=row, column=1, sticky='w')
        setattr(self, f"{layer_type}_label", label)

    def create_text_entries(self, parent):
        entries = [
            ("Name:", 'name_entry', 4, 50, []),
            ("Type:", 'type_combobox', 5, None, ["Item", "Armor", "Weapon"]),
            ("Details:", 'details_entry', 6, 50, []),
            ("Rarity:", 'rarity_combobox', 7, None, ["Artifact", "Common", "Uncommon", "Rare", "Very Rare", "Legendary", "Unknown"]),
            ("Description:", 'description_text', 8, None, [])
        ]

        for label_text, widget_name, row, limit, values in entries:
            tk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=5)
            if values:
                combobox = Combobox(parent, values=values, state="readonly")
                combobox.grid(row=row, column=1, padx=5, pady=5, sticky='w')
                setattr(self, widget_name, combobox)
            else:
                widget = tk.Text(parent, width=30, height=5, wrap="word") if widget_name == 'description_text' else tk.Entry(parent, width=30)
                widget.grid(row=row, column=1, padx=5, pady=5, sticky='w')
                setattr(self, widget_name, widget)
                if widget_name == 'description_text':
                    widget.bind("<KeyRelease>", self.check_description_length)

    def create_action_buttons(self, parent):
        buttons = [
            ("Preview Card", self.preview_card, 0, 'preview_button'),
            ("Create Card", self.create_card, 1, 'create_card_button')
        ]
        for text, command, column, attr in buttons:
            button = tk.Button(parent, text=text, command=command, state=tk.DISABLED)
            button.grid(row=10, column=column, pady=10, padx=5 if column == 0 else 15, sticky='w')
            setattr(self, attr, button)

    def load_file(self, layer_type):
        filetypes = {
            'background_image': [("Image files", "*.png *.jpg *.jpeg")],
            'card_art': [("Image files", "*.png *.jpg *.jpeg")],
            'font_a': [("Font files", "*.ttf *.otf")],
            'font_b': [("Font files", "*.ttf *.otf")]
        }
        file_path = filedialog.askopenfilename(filetypes=filetypes.get(layer_type, []))
        if file_path:
            self.paths[layer_type] = file_path
            getattr(self, f"{layer_type}_label").config(text=os.path.basename(file_path) + " ✓")
            self.update_buttons_state()

    def update_buttons_state(self):
        all_resources_loaded = all(self.paths[resource] for resource in ('background_image', 'font_a', 'font_b'))
        state = tk.NORMAL if all_resources_loaded else tk.DISABLED
        self.preview_button.config(state=state)
        self.create_card_button.config(state=state)

    def validate_fields(self):
        if not self.name_entry.get():
            messagebox.showerror("Error", "Name cannot be empty.")
            return False
        if not self.rarity_combobox.get():
            messagebox.showerror("Error", "Please select a rarity.")
            return False
        if not self.paths['background_image']:
            messagebox.showerror("Error", "Background image not loaded.")
            return False
        return True

    def preview_card(self):
        if not self.validate_fields():
            return
        card = self.generate_card()
        if card:
            card.thumbnail((300, 420))
            card_image = ImageTk.PhotoImage(card)
            self.preview_panel.config(image=card_image)
            self.preview_panel.image = card_image

    def create_card(self):
        if not self.validate_fields():
            return
        card = self.generate_card()
        if card:
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf")])
            if save_path:
                card.save(save_path)
                messagebox.showinfo("Card Created", f"Card saved as {save_path}")

    def generate_card(self):
        try:
            background_image = Image.open(self.paths['background_image'])
            card_art_image = Image.open(self.paths['card_art']) if self.paths['card_art'] else None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load images: {str(e)}")
            return None

        card = Image.new("RGBA", (750, 1050))
        if card_art_image:
            card.paste(card_art_image, (0, 0))
        card.paste(background_image, (0, 0), background_image)
        draw = ImageDraw.Draw(card)

        # Load fonts
        font_a = self.load_font(self.paths['font_a'], 40)
        font_b = self.load_font(self.paths['font_b'], 40)

        # Draw text fields
        text_entries = [
            ("Name", self.name_entry.get(), font_a, (43, 52, 707, 108), 40, None, True, True),  # Moved Name 3 pixels lower from previous position
            ("Type", self.type_combobox.get(), font_a, (51, 561, 188, 617), 22, 22, False, False),  # Moved Type up by 3 pixels, fixed size 22
            ("Details", self.details_entry.get(), font_a, (235, 561, 515, 617), 25, None, True, False),  # Moved Details up by 3 pixels, max size 25
            ("Rarity", self.rarity_combobox.get(), font_a, (561, 561, 698, 617), 22, 22, False, False),  # Moved Rarity up by 3 pixels, fixed size 22
            ("Description", self.description_text.get("1.0", "end-1c"), font_b, (49, 644, 701, 968), 40, None, True, True)
        ]
        for field_name, text, font, box, max_font_size, fixed_font_size, adjust_font, left_justified in text_entries:
            self.draw_text(draw, field_name, text, font, box, max_font_size=max_font_size, fixed_font_size=fixed_font_size, adjust_font_size=adjust_font, left_justified=left_justified)

        return card

    def load_font(self, font_path, size):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception as e:
            print(f"Failed to load font: {e}")
            return ImageFont.load_default()

    def draw_text(self, draw, field_name, text, font, box, max_font_size=None, fixed_font_size=None, adjust_font_size=False, left_justified=False):
        if not text:
            return

        max_font_size = max_font_size or font.size
        adjusted_font = font

        # Use fixed font size if provided
        if fixed_font_size:
            adjusted_font = ImageFont.truetype(font.path, fixed_font_size)
        else:
            # Adjust font size to fit the box horizontally or vertically as needed
            if field_name in ["Name", "Details"]:
                max_width = box[2] - box[0]
                while adjusted_font.size > 12 and draw.textbbox((0, 0), text, font=adjusted_font)[2] > max_width:
                    adjusted_font = ImageFont.truetype(adjusted_font.path, adjusted_font.size - 1)
            elif field_name == "Description":
                max_height = box[3] - box[1]
                wrapped_text = self.wrap_text(draw, text, adjusted_font, box[2] - box[0], respect_formatting=True)
                total_height = sum(draw.textbbox((0, 0), line, font=adjusted_font)[3] for line in wrapped_text.splitlines())
                while adjusted_font.size > 12 and total_height > max_height:
                    adjusted_font = ImageFont.truetype(adjusted_font.path, adjusted_font.size - 1)
                    wrapped_text = self.wrap_text(draw, text, adjusted_font, box[2] - box[0], respect_formatting=True)
                    total_height = sum(draw.textbbox((0, 0), line, font=adjusted_font)[3] for line in wrapped_text.splitlines())

        # Set adjusted font for text drawing
        font = adjusted_font

        if font.size <= 12:
            self.show_warning(field_name)

        if field_name == "Description":
            self.draw_wrapped_text(draw, box, text, font, respect_formatting=True)
        else:
            self.draw_centered_text(draw, box, text, font)

    def draw_centered_text(self, draw, box, text, font):
        box_x0, box_y0, box_x1, box_y1 = box
        text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
        x = box_x0 + (box_x1 - box_x0 - text_width) / 2
        y = box_y0 + (box_y1 - box_y0 - text_height) / 2
        draw.text((x, y), text, font=font, fill="black")

    def draw_wrapped_text(self, draw, box, text, font, respect_formatting=False):
        box_x0, box_y0, box_x1, box_y1 = box
        max_width = box_x1 - box_x0
        max_height = box_y1 - box_y0

        # Adjust font size until text fits within the bounding box
        wrapped_text = self.wrap_text(draw, text, font, max_width, respect_formatting=respect_formatting)
        total_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in wrapped_text.splitlines())

        while font.size > 12 and total_height > max_height:
            font = ImageFont.truetype(font.path, font.size - 1)
            wrapped_text = self.wrap_text(draw, text, font, max_width, respect_formatting=respect_formatting)
            total_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in wrapped_text.splitlines())

        # Set background warning if the font size reaches 12
        if font.size <= 12:
            self.description_text.config(bg='#ffdddd')  # Light red background for warning
            self.show_warning_tooltip("Warning: Too much text. Please shorten the description.")
        else:
            self.description_text.config(bg='white')  # Reset background if size is acceptable

        # Draw the wrapped text
        y_offset = box_y0
        for line in wrapped_text.splitlines():
            draw.text((box_x0, y_offset), line, font=font, fill="black")
            y_offset += draw.textbbox((0, 0), line, font=font)[3] + 4  # Add spacing between lines

    def adjust_font_size(self, draw, text, font, box, max_font_size):
        # Adjust font size until the entire text fits within the box
        max_width = box[2] - box[0]
        max_height = box[3] - box[1]

        adjusted_font = ImageFont.truetype(font.path, max_font_size) if font else ImageFont.load_default()

        while adjusted_font.size > 12:
            wrapped_text = self.wrap_text(draw, text, adjusted_font, max_width, respect_formatting=True)
            total_height = sum(draw.textbbox((0, 0), line, font=adjusted_font)[3] for line in wrapped_text.splitlines())

            if total_height <= max_height:
                break
            adjusted_font = ImageFont.truetype(font.path, adjusted_font.size - 1)

        return adjusted_font

    def wrap_text(self, draw, text, font, max_width, respect_formatting=False):
        if respect_formatting:
            lines = text.splitlines()
            wrapped_lines = []
            for line in lines:
                words = line.split()
                current_line = ""
                for word in words:
                    test_line = f"{current_line} {word}".strip()
                    if draw.textbbox((0, 0), test_line, font=font)[2] <= max_width:
                        current_line = test_line
                    else:
                        wrapped_lines.append(current_line)
                        current_line = word
                wrapped_lines.append(current_line)
            return "\n".join(wrapped_lines)
        else:
            words = text.split()
            lines, current_line = [], ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                if draw.textbbox((0, 0), test_line, font=font)[2] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)
            return "\n".join(lines)

    def check_description_length(self, event):
        content = self.description_text.get("1.0", "end-1c")
        draw = ImageDraw.Draw(Image.new("RGBA", (750, 1050)))
        font = self.load_font(self.paths['font_b'], 40)
        adjusted_font = self.adjust_font_size(draw, content, font, (49, 644, 701, 968), 40)
        if adjusted_font.size <= 12:
            self.description_text.config(bg='#ffdddd')
        else:
            self.description_text.config(bg='white')

    def show_warning_tooltip(self, message):
        if hasattr(self, 'warning_label') and self.warning_label:
            self.warning_label.destroy()
        self.warning_label = tk.Label(self.root, text=message, font=("Helvetica", 8), fg="red", bg='#ffdddd')
        self.warning_label.pack(anchor='w', padx=5, pady=2)
        self.root.after(5000, self.warning_label.destroy)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = CardCreatorApp(root)
        root.mainloop()
    except Exception as e:
        print("An error occurred:")
        print(traceback.format_exc())
        with open("error_log.txt", "w") as error_file:
            error_file.write(traceback.format_exc())
        input("Press Enter to exit...")