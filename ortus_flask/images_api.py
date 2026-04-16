"""
Blog Image API Blueprint.
Provides endpoints for uploading and managing blog cover images.
"""

import os
import uuid
import logging
from flask import Blueprint, request, jsonify, current_app, send_from_directory

logger = logging.getLogger(__name__)


def create_image_api_blueprint():
    """
    Create blog image API blueprint.
    
    Returns:
        Flask Blueprint
    """
    
    images_bp = Blueprint("ortus_images", __name__, url_prefix="/api/images")
    
    @images_bp.route("/upload", methods=["POST"])
    def upload_image():
        try:
            if 'image' not in request.files:
                return jsonify({"error": "No image file provided"}), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
            ext = os.path.splitext(file.filename)[1].lower()
            allowed_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
            
            if ext not in allowed_exts:
                return jsonify({"error": "Invalid file type"}), 400
            
            filename = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            image_url = f"/api/images/view/{filename}"
            
            return jsonify({
                "url": image_url,
                "filename": filename
            }), 201
            
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return jsonify({"error": str(e)}), 500
    
    @images_bp.route("/editorjs", methods=["POST"])
    def upload_editorjs_image():
        try:
            file = request.files.get('image') or request.files.get('file')
            if not file or file.filename == '':
                return jsonify({"error": "No image file provided"}), 400
            
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
            ext = os.path.splitext(file.filename)[1].lower()
            allowed_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
            
            if ext not in allowed_exts:
                return jsonify({"error": "Invalid file type"}), 400
            
            filename = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            image_url = f"/api/images/view/{filename}"
            
            return jsonify({
                "success": 1,
                "file": {
                    "url": image_url
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Error uploading EditorJS image: {e}")
            return jsonify({
                "success": 0,
                "error": str(e)
            }), 500
    
    @images_bp.route("/view/<filename>", methods=["GET"])
    def get_image(filename):
        try:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            return send_from_directory(upload_folder, filename)
        except Exception as e:
            return jsonify({"error": "Image not found"}), 404
    
    @images_bp.route("/delete/<filename>", methods=["DELETE"])
    def delete_image(filename):
        try:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            filepath = os.path.join(upload_folder, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                return jsonify({"msg": "Image deleted"}), 200
            else:
                return jsonify({"error": "Image not found"}), 404
                
        except Exception as e:
            logger.error(f"Error deleting image: {e}")
            return jsonify({"error": str(e)}), 500
    
    return images_bp
