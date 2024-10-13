import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox, Label
from PIL import Image, ImageDraw, ImageFont, ImageTk
import webbrowser
import traceback

class Creator:
    def __init__(self, fontA, fontB, background, art):
        # Paths for fonts and graphics
        self.paths = {
            'font_a': fontA,
            'font_b': fontB,
            'background_image': background,
            'card_art': art
        }

    def generate_card(self, name, type, details, rarity, description):
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
            ("Name", name, font_a, (43, 52, 707, 108), 40, None, True, True),  # Moved Name 3 pixels lower from previous position
            ("Type", type, font_a, (51, 561, 188, 617), 22, 22, False, False),  # Moved Type up by 3 pixels, fixed size 22
            ("Details", details, font_a, (235, 561, 515, 617), 25, None, True, False),  # Moved Details up by 3 pixels, max size 25
            ("Rarity", rarity, font_a, (561, 561, 698, 617), 22, 22, False, False),  # Moved Rarity up by 3 pixels, fixed size 22
            ("Description", description, font_b, (49, 644, 701, 968), 40, None, True, True)
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