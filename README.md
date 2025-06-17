# Fake Invoice Hashing & Detection Web App

## Project Overview

This project is a web-based tool for detecting fake invoices using SHA256 image hashing. It leverages a database of legitimate invoice hashes to verify uploaded invoices. The system is built with Flask and includes scripts for database management, testing, and analysis. The goal is to help businesses and individuals quickly verify the authenticity of invoice images and protect against fraud.

---

## Features
- **Web Interface:** User-friendly web app for uploading and verifying invoices.
- **SHA256 Hashing:** Each invoice image is hashed and checked against a database of legitimate invoices.
- **Database Management:** Scripts to build, analyze, and test the hash database.
- **Statistics & Reporting:** View database stats and download verification reports.
- **Modern UI:** Responsive design with drag-and-drop upload, real-time feedback, and detailed results.

---

## Getting Started

### 1. Clone the Repository
Clone the repository to your local machine:
```bash
git clone https://github.com/qasim233/Detecting_Fake_Invoices_Using_hashing
cd Hashing_On_Invoice
```

### 2. Create and Activate a Virtual Environment
**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```
**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Requirements
Install all required Python packages:
```bash
pip install -r requirements.txt
```

---

## Project Structure & File Explanations

```

├── app.py                        # Main Flask web application
├── requirements.txt              # Python dependencies
├── legitimate_invoice_hashes.pkl # Pickle file with legitimate invoice hashes and metadata
├── legitimate_invoice_hashes.json# Human-readable summary of legitimate hashes
│
├── scripts/                      # Utility and core scripts
│   ├── invoice_detector.py       # Core logic for hash database and detection
│   ├── analyze_database.py       # Analyze hash database and output stats
│   ├── debug_dataset.py          # Inspect dataset structure
│   └── test_detector.py          # Test the invoice detector
│
├── images/                       # Invoice images and ground truth
│   ├── train/                    # Training images and ground truth
│   ├── test/                     # Test images and ground truth
│   └── validation/               # Validation images and ground truth
│
├── static/                       # Static files for the web interface
│   ├── css/style.css             # Stylesheet
│   └── js/script.js              # JavaScript for UI and AJAX
│
├── templates/                    # HTML templates
│   └── index.html                # Main web interface template
│
└── .venv/                        # Python virtual environment (not uploaded to GitHub)
```

### File/Directory Details and Dataset
- **app.py**: Main entry point. Runs the Flask server, handles uploads, and performs invoice verification.
- **requirements.txt**: Lists all Python dependencies.
- **legitimate_invoice_hashes.pkl**: Binary file storing SHA256 hashes and metadata for legitimate invoices.
- **legitimate_invoice_hashes.json**: JSON summary of the hash database for inspection.
Note: The invoice data is taken from Hugging face datasets named: **"katanaml-org/invoices-donut-data-v1"**

#### scripts/
- **invoice_detector.py**: Build, save, load, and check invoice image hashes. Also builds the hash database from datasets.
- **analyze_database.py**: Analyze the hash database, providing statistics and saving a summary report.
- **debug_dataset.py**: Inspect the structure of invoice datasets for debugging.
- **test_detector.py**: Test the invoice detector on both legitimate and synthetic (fake) invoices.

#### images/
- **train/**, **test/**, **validation/**: Each contains invoice images (`*_image_*.png`) and ground truth files (`*_gt_*.txt`) in JSON format.

#### static/
- **css/style.css**: Stylesheet for the web interface.
- **js/script.js**: JavaScript for handling uploads, AJAX, and UI updates.

#### templates/
- **index.html**: Main HTML template for the web interface.

#### .venv/
- Standard Python virtual environment directory. **Not included in the repository.**

---

## How It Works

1. **Database Creation:**
   - Use `scripts/invoice_detector.py` to build a database of SHA256 hashes from a dataset of legitimate invoices. This creates/updates `legitimate_invoice_hashes.pkl` and `legitimate_invoice_hashes.json`.
   - Example:
     ```bash
     python scripts/invoice_detector.py
     ```

2. **Web Interface:**
   - Run `app.py` to start the Flask server:
     ```bash
     python app.py
     ```
   - Open your browser and go to [http://localhost:5000](http://localhost:5000)
   - Upload an invoice image. The app will compute its SHA256 hash and check it against the database.

3. **Detection:**
   - If the hash matches a legitimate invoice, it is marked as legitimate; otherwise, it is flagged as potentially fake.
   - The result, hash, confidence, and analysis are displayed in the web interface.

4. **Testing and Analysis:**
   - Use `scripts/test_detector.py` to test the system with real and synthetic invoices.
   - Use `scripts/analyze_database.py` to analyze the hash database and generate statistics.

---

## Usage Example

1. **(Optional) Create/Update the hash database:**
   ```bash
   python scripts/invoice_detector.py
   ```
2. **Run the web app:**
   ```bash
   python app.py
   ```
3. **Access the web interface:**
   Open your browser and go to [http://localhost:5000](http://localhost:5000)
4. **Test the detector:**
   ```bash
   python scripts/test_detector.py
   ```
5. **Analyze the database:**
   ```bash
   python scripts/analyze_database.py
   ```

---

## Notes
- The `.venv` directory is for local development only and should **not** be committed to GitHub.
- Always use your own virtual environment and install dependencies as described above.
- For production, consider using environment variables for secrets and configuration.
- The hash database must be created before using the web app for detection.

---

## Requirements

The main dependencies are:
- Flask
- Pillow
- transformers
- torch
- Werkzeug
- datasets

Install all dependencies with:
```bash
pip install -r requirements.txt
```
---

## Contact
For questions or support, please open an issue or contact the maintainer. 
