import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk
import qrcode
import json
from qrcode.image.styles.moduledrawers.pil import SquareModuleDrawer
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer, VerticalBarsDrawer, HorizontalBarsDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask, SolidFillColorMask, HorizontalGradiantColorMask
from PIL import Image
import io
import cairosvg
import svgwrite

class QRGeneratorWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="QR Code Generator")
        self.set_border_width(10)
        self.set_default_size(600, 800) # Increased size for better layout

        # Main container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Text input
        self.text_entry = Gtk.Entry()
        self.text_entry.set_placeholder_text("Enter text for QR code")
        vbox.pack_start(self.text_entry, False, True, 0)

        # Style options in a grid
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        vbox.pack_start(grid, False, True, 10)

        # QR Code name for saving/loading
        self.name_entry = Gtk.Entry()
        self.name_entry.set_placeholder_text("Enter QR code name to save/load")
        grid.attach(self.name_entry, 0, 0, 4, 1)

        # Color choosers
        self.fg_color_button = Gtk.ColorButton()
        self.fg_color_button.set_rgba(Gdk.RGBA(0, 0, 0, 1))
        grid.attach(Gtk.Label(label="QR Color:"), 0, 8, 1, 1)
        grid.attach(self.fg_color_button, 1, 8, 1, 1)

        self.bg_color_button = Gtk.ColorButton()
        self.bg_color_button.set_rgba(Gdk.RGBA(1, 1, 1, 1))
        grid.attach(Gtk.Label(label="Background:"), 2, 8, 1, 1)
        grid.attach(self.bg_color_button, 3, 8, 1, 1)

        # Body shape combo
        self.body_combo = Gtk.ComboBoxText()
        for style in ["Square", "Circle", "Rounded", "Vertical Bars", "Horizontal Bars", 
                     "Dots", "Lines", "Cross", "Stars"]:
            self.body_combo.append_text(style)
        self.body_combo.set_active(0)
        grid.attach(Gtk.Label(label="Body Shape:"), 0, 1, 1, 1)
        grid.attach(self.body_combo, 1, 1, 1, 1)

        # Eye shape combo
        self.eye_combo = Gtk.ComboBoxText()
        for style in ["Square", "Circle", "Rounded", "Diamonds", "Leaves", 
                     "Shield", "Curved"]:
            self.eye_combo.append_text(style)
        self.eye_combo.set_active(0)
        grid.attach(Gtk.Label(label="Eye Shape:"), 2, 1, 1, 1)
        grid.attach(self.eye_combo, 3, 1, 1, 1)

        # Eye frame combo (Fixed:  Added more options for Eye Frame)
        self.eye_frame_combo = Gtk.ComboBoxText()
        for style in ["None", "Square", "Circle", "Rounded", "Fancy", "Double"]: #Added "None" option
            self.eye_frame_combo.append_text(style)
        self.eye_frame_combo.set_active(0)
        grid.attach(Gtk.Label(label="Eye Frame:"), 0, 2, 1, 1)
        grid.attach(self.eye_frame_combo, 1, 2, 1, 1)

        # Logo controls
        logo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.logo_button = Gtk.Button(label="Select Logo")
        self.logo_button.connect("clicked", self.on_logo_clicked)
        self.remove_logo_button = Gtk.Button(label="Remove Logo")
        self.remove_logo_button.connect("clicked", self.on_remove_logo_clicked)
        logo_box.pack_start(self.logo_button, True, True, 0)
        logo_box.pack_start(self.remove_logo_button, True, True, 0)
        grid.attach(logo_box, 0, 3, 4, 1)

        # QR Code quality/size adjustment
        self.qr_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 200, 2000, 100)
        self.qr_scale.set_value(500)  # Default value increased for better quality
        grid.attach(Gtk.Label(label="QR Code Size (px):"), 0, 4, 1, 1)
        grid.attach(self.qr_scale, 1, 4, 3, 1)

        self.logo_size_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 10, 50, 1)
        self.logo_size_scale.set_value(30)
        grid.attach(Gtk.Label(label="Logo Size (%):"), 0, 5, 1, 1)
        grid.attach(self.logo_size_scale, 1, 5, 3, 1)

        self.logo_radius = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 50, 1)
        self.logo_radius.set_value(0)
        grid.attach(Gtk.Label(label="Logo Corner Radius:"), 0, 6, 1, 1)
        grid.attach(self.logo_radius, 1, 6, 3, 1)

        # Export format combo (Fixed: Moved to prevent overlap)
        self.export_combo = Gtk.ComboBoxText()
        for format in ["PNG", "SVG", "PDF"]:
            self.export_combo.append_text(format)
        self.export_combo.set_active(0)
        grid.attach(Gtk.Label(label="Export Format:"), 0, 7, 1, 1)
        grid.attach(self.export_combo, 1, 7, 1, 1)


        # Generate and Export buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        generate_button = Gtk.Button(label="Generate QR Code")
        generate_button.connect("clicked", self.on_generate_clicked)
        export_button = Gtk.Button(label="Export")
        export_button.connect("clicked", self.on_export_clicked)
        button_box.pack_start(generate_button, True, True, 0)
        button_box.pack_start(export_button, True, True, 0)
        vbox.pack_start(button_box, False, True, 0)

        # Status message
        self.status_label = Gtk.Label()
        vbox.pack_start(self.status_label, False, True, 5)

        # Image display
        self.image = Gtk.Image()
        vbox.pack_start(self.image, True, True, 0)

        self.logo_path = None
        self.qr_image = None
        self.qr_codes = {}
        self.load_qr_codes()

        # Save/Load buttons
        save_load_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        save_button = Gtk.Button(label="Save QR Code")
        save_button.connect("clicked", self.on_save_clicked)
        load_button = Gtk.Button(label="Load QR Code")
        load_button.connect("clicked", self.on_load_clicked)
        save_load_box.pack_start(save_button, True, True, 0)
        save_load_box.pack_start(load_button, True, True, 0)
        vbox.pack_start(save_load_box, False, True, 0)

    def load_qr_codes(self):
        try:
            with open('qr_codes.json', 'r') as f:
                self.qr_codes = json.load(f)
        except:
            self.qr_codes = {}

    def save_qr_codes(self):
        with open('qr_codes.json', 'w') as f:
            json.dump(self.qr_codes, f)

    def on_save_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Save QR Code Configuration",
            parent=self,
            action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        
        dialog.set_current_name("qrcode_config.json")
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            save_path = dialog.get_filename()
            config = {
                'text': self.text_entry.get_text(),
                'body_style': self.body_combo.get_active_text(),
                'eye_style': self.eye_combo.get_active_text(),
                'eye_frame': self.eye_frame_combo.get_active_text(),
                'logo_path': self.logo_path,
                'qr_size': self.qr_scale.get_value(),
                'logo_size': self.logo_size_scale.get_value(),
                'logo_radius': self.logo_radius.get_value(),
                'fg_color': self.get_color_hex(self.fg_color_button),
                'bg_color': self.get_color_hex(self.bg_color_button)
            }
            with open(save_path, 'w') as f:
                json.dump(config, f)
            self.status_label.set_text(f"QR code configuration saved to {save_path}")
        
        dialog.destroy()


    def set_combo_by_text(self, combo, text):
        model = combo.get_model()
        for i, item in enumerate(model):
            if item[0] == text:
                combo.set_active(i)
                break

    def on_load_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Load QR Code Configuration",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        filter_json = Gtk.FileFilter()
        filter_json.set_name("JSON files")
        filter_json.add_pattern("*.json")
        dialog.add_filter(filter_json)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            load_path = dialog.get_filename()
            try:
                with open(load_path, 'r') as f:
                    data = json.load(f)
                self.text_entry.set_text(data['text'])
                self.set_combo_by_text(self.body_combo, data['body_style'])
                self.set_combo_by_text(self.eye_combo, data['eye_style'])
                self.set_combo_by_text(self.eye_frame_combo, data['eye_frame'])
                self.logo_path = data['logo_path']
                self.qr_scale.set_value(data['qr_size'])
                self.logo_size_scale.set_value(data['logo_size'])
                self.logo_radius.set_value(data['logo_radius'])

                fg_color = Gdk.RGBA()
                fg_color.parse(data['fg_color'])
                self.fg_color_button.set_rgba(fg_color)

                bg_color = Gdk.RGBA()
                bg_color.parse(data['bg_color'])
                self.bg_color_button.set_rgba(bg_color)

                self.on_generate_clicked(None)
                self.status_label.set_text(f"QR code configuration loaded successfully!")
            except Exception as e:
                self.status_label.set_text(f"Error loading QR code: {e}")
        
        dialog.destroy()

    def get_color_hex(self, color_button):
        rgba = color_button.get_rgba()
        return '#{:02x}{:02x}{:02x}'.format(
            int(rgba.red * 255),
            int(rgba.green * 255),
            int(rgba.blue * 255)
        )

    def on_logo_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Choose a Logo", parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )

        filter_images = Gtk.FileFilter()
        filter_images.set_name("Image files")
        filter_images.add_mime_type("image/*")
        dialog.add_filter(filter_images)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.logo_path = dialog.get_filename()
            self.on_generate_clicked(None)
        dialog.destroy()

    def on_generate_clicked(self, widget):
        if not self.text_entry.get_text():
            self.status_label.set_text("Please enter some data first!")
            return

        try:
            # Get styles from UI
            body_style = self.body_combo.get_active_text()
            eye_style = self.eye_combo.get_active_text()
            eye_frame_style = self.eye_frame_combo.get_active_text()

            # Create module drawers for each part
            body_drawer = self._get_module_drawer(body_style)
            eye_drawer = self._get_module_drawer(eye_style)
            eye_frame_drawer = self._get_module_drawer(eye_frame_style)

            # Create color mask
            color_mask = RadialGradiantColorMask(
                back_color=(255, 255, 255),
                center_color=(0, 0, 0),
                edge_color=(0, 0, 0)
            )

            # Create QR code with styled image
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )

            qr.add_data(self.text_entry.get_text())
            qr.make(fit=True)

            # Create styled image
            self.qr_image = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=body_drawer,
                eye_drawer=eye_drawer,
                eye_frame_drawer=eye_frame_drawer,
                color_mask=color_mask
            )

            # Add logo if selected
            if self.logo_path:
                logo = Image.open(self.logo_path)
                logo = logo.convert("RGBA")

                # Optimize logo processing
                size_percent = self.logo_size_scale.get_value() / 100
                basewidth = int(self.qr_image.size[0] * size_percent)
                wpercent = (basewidth / float(logo.size[0]))
                hsize = int((float(logo.size[1]) * float(wpercent)))
                logo = logo.resize((basewidth, hsize), Image.Resampling.LANCZOS)

                if self.logo_radius.get_value() > 0:
                    from PIL import ImageDraw
                    mask = Image.new('L', logo.size, 0)
                    draw = ImageDraw.Draw(mask)
                    radius = int(self.logo_radius.get_value())
                    draw.rounded_rectangle([0, 0, logo.size[0], logo.size[1]], radius, fill=255)
                    logo.putalpha(mask)

                pos = ((self.qr_image.size[0] - logo.size[0]) // 2,
                    (self.qr_image.size[1] - logo.size[1]) // 2)

                self.qr_image.paste(logo, pos, logo)

            # Optimize preview display
            self.status_label.set_text("Generating preview...")
            while Gtk.events_pending():
                Gtk.main_iteration()

            buffer = io.BytesIO()
            preview_size = (300, 300)
            preview_image = self.qr_image.copy()
            preview_image.thumbnail(preview_size, Image.Resampling.LANCZOS)
            preview_image.save(buffer, format='PNG', optimize=True)
            buffer.seek(0)

            loader = GdkPixbuf.PixbufLoader.new_with_type('png')
            loader.write(buffer.read())
            loader.close()

            pixbuf = loader.get_pixbuf()
            self.image.set_from_pixbuf(pixbuf)
            self.status_label.set_text("QR code generated successfully!")

        except Exception as e:
            self.status_label.set_text(f"Error generating QR code: {e}")

    def on_remove_logo_clicked(self, widget):
        self.status_label.set_text("Removing logo...")
        while Gtk.events_pending():
            Gtk.main_iteration()
        
        self.logo_path = None
        self.on_generate_clicked(None)

    def on_export_clicked(self, widget):
        if not self.qr_image:
            return

        dialog = Gtk.FileChooserDialog(
            title="Save QR Code",
            parent=self,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK,
        )

        format = self.export_combo.get_active_text().lower()
        dialog.set_current_name(f"qrcode.{format}")

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            try:
                self.qr_image.save(filename, format=format.upper())
                self.status_label.set_text(f"QR code exported to '{filename}' successfully!")
            except Exception as e:
                self.status_label.set_text(f"Error exporting QR code: {e}")

        dialog.destroy()

    def _get_module_drawer(self, style):
        if style == "Circle":
            return CircleModuleDrawer(radius_ratio=0.75)
        elif style == "Rounded":
            return RoundedModuleDrawer(radius_ratio=0.9)
        elif style == "Vertical Bars":
            return VerticalBarsDrawer(horizontal_shrink=0.5)
        elif style == "Horizontal Bars":
            return HorizontalBarsDrawer(vertical_shrink=0.5)
        elif style == "Dots":
            return CircleModuleDrawer(radius_ratio=0.3)
        elif style == "Lines":
            return HorizontalBarsDrawer(vertical_shrink=0.8)
        elif style == "Cross":
            return CircleModuleDrawer(radius_ratio=0.1)
        elif style == "Stars":
            return CircleModuleDrawer(radius_ratio=0.9, points=5)
        elif style == "Diamonds":
            return RoundedModuleDrawer(radius_ratio=0.5)
        elif style == "Shield":
            return RoundedModuleDrawer(radius_ratio=0.8)
        elif style == "Curved":
            return RoundedModuleDrawer(radius_ratio=0.6)
        elif style == "Leaves":
            return CircleModuleDrawer(radius_ratio=0.8, points=3)
        else:
            return SquareModuleDrawer()

win = QRGeneratorWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()