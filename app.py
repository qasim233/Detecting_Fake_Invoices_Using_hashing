from flask import Flask, request, render_template, jsonify, redirect, url_for
import os
import io
import base64
from PIL import Image
from scripts.invoice_detector import InvoiceHashDetector
import logging
from werkzeug.utils import secure_filename

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize the detector
detector = InvoiceHashDetector()

# Load the hash database on startup
def load_detector():
    global detector
    try:
        if not detector.load_hash_database():
            logger.warning("Hash database not found. Please run invoice_detector.py first.")
        else:
            logger.info("Invoice detector loaded successfully!")
    except Exception as e:
        logger.error(f"Error loading detector: {e}")

load_detector()

def allowed_file(filename):
    """Check if the uploaded file is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and invoice detection"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an image file.'}), 400
        
        # Read and process the image
        image_data = file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Detect if the invoice is fake
        result = detector.detect_fake_invoice(image)
        
        # Convert image to base64 for display
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG', quality=85)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Prepare response
        response = {
            'success': True,
            'result': result,
            'image': f"data:image/jpeg;base64,{img_base64}",
            'filename': secure_filename(file.filename)
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@app.route('/stats')
def get_stats():
    """Get database statistics"""
    try:
        stats = detector.get_database_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database_loaded': len(detector.legitimate_hashes) > 0
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
