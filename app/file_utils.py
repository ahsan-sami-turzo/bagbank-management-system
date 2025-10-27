# app/file_utils.py

import os
from werkzeug.utils import secure_filename
from PIL import Image
from flask import current_app
import re

# --- Constants from Config ---
def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def slugify(text):
    """Converts text to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text).strip() # Remove non-word characters
    text = re.sub(r'[-\s]+', '-', text)       # Replace spaces and hyphens with a single hyphen
    return text

def save_and_process_image(file_storage, product_slug, filename_prefix):
    """
    Saves and processes an image: checks security, resizes to 1:1, compresses, 
    and saves to a slug-based directory.
    
    Returns: The relative file path on success, or None on failure.
    """
    if not file_storage or not file_storage.filename or not allowed_file(file_storage.filename):
        return None

    # 1. Prepare Paths
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], product_slug)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Secure the original filename and generate a new name
    original_ext = file_storage.filename.rsplit('.', 1)[1].lower()
    safe_filename = secure_filename(file_storage.filename)
    # New filename format: prefix-timestamp-safe_filename.ext
    new_filename = f"{filename_prefix}-{os.urandom(8).hex()[:6]}.{original_ext}"
    full_path = os.path.join(upload_dir, new_filename)
    
    # Save the temporary file (Pillow needs a path or file handle)
    temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp_' + new_filename)
    file_storage.save(temp_path)

    try:
        # 2. Process Image (Resize 1:1 and Compress Losslessly)
        img = Image.open(temp_path).convert('RGB')
        target_size = current_app.config['IMAGE_SIZE']

        # Crop to 1:1 aspect ratio (square center crop)
        width, height = img.size
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = (width + min_dim) // 2
        bottom = (height + min_dim) // 2
        img = img.crop((left, top, right, bottom))

        # Resize to target size (e.g., 800x800)
        img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
        
        # Save compressed (JPEG uses quality for compression)
        # Use relative path for database storage: product-slug/filename.ext
        relative_path = os.path.join(product_slug, new_filename)

        if original_ext in ['jpg', 'jpeg']:
            # JPEG: Use quality=95 for near-lossless compression
            img.save(full_path, 'JPEG', quality=95, optimize=True)
        elif original_ext == 'png':
            # PNG: Optimization is considered lossless compression
            img.save(full_path, 'PNG', optimize=True)
        else:
            img.save(full_path)

        return relative_path

    except Exception as e:
        current_app.logger.error(f"Image processing failed: {e}")
        return None
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)