# qrcg

A modern, customizable QR code generator built with Python and GTK. Create unique QR codes with custom shapes, colors, and logos.


## Features

- Customizable QR code body, eye, and eye frame shapes
- Logo integration with size and corner radius control
- Export to various image formats (PNG, JPG, SVG)
- Real-time preview generation
- Modern GTK interface


## Installation

1. Clone the repository:
```bash
git clone https://github.com/cristian158/QRCode-Generator.git
cd QRCode-Generator
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Enter your data in the text field

3. Customize the QR code appearance:
- Select body shape from the dropdown
- Choose eye shape from the dropdown
- Pick eye frame style from the dropdown

4. Add a logo (optional):
- Click "Add Logo" to select an image
- Adjust logo size and corner radius

5. Generate the QR code by clicking "Generate"

6. Export the QR code by clicking "Export"


## Requirements

Python 3.8+
GTK 3+
PIL (Python Imaging Library)
qrcode library
License
This project is licensed under the MIT License - see the LICENSE file for details.