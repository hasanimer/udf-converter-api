from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import tempfile
import subprocess
import logging

app = Flask(__name__)
CORS(app, origins=["https://imer.av.tr", "https://*.vercel.app", "http://localhost:3000"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return jsonify({
        'status': 'UDF Converter API',
        'version': '2.0',
        'endpoints': {
            '/convert': 'POST - UDF → PDF/DOCX',
            '/convert-to-udf': 'POST - DOCX/PDF → UDF',
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/convert', methods=['POST'])
def convert():
    """UDF → PDF/DOCX dönüştürme"""
    try:
        if 'file' not in request.files:
            logger.error('Dosya bulunamadı')
            return jsonify({'error': 'Dosya bulunamadı'}), 400
        
        file = request.files['file']
        format_type = request.form.get('format', 'pdf')
        
        if not file.filename:
            return jsonify({'error': 'Dosya adı geçersiz'}), 400
        
        logger.info(f'Dönüştürme başlıyor: {file.filename} -> {format_type}')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.udf') as tmp:
            file.save(tmp.name)
            input_path = tmp.name
        
        if format_type == 'pdf':
            script = 'udf_to_pdf.py'
            output_ext = 'pdf'
            mime_type = 'application/pdf'
        elif format_type == 'docx':
            script = 'udf_to_docx.py'
            output_ext = 'docx'
            mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            return jsonify({'error': 'Geçersiz format (pdf veya docx olmalı)'}), 400
        
        result = subprocess.run(
            ['python3', script, input_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            logger.error(f'Script hatası: {result.stderr}')
            return jsonify({'error': 'Dönüştürme başarısız', 'details': result.stderr}), 500
        
        output_path = input_path.replace('.udf', f'.{output_ext}')
        
        if not os.path.exists(output_path):
            logger.error('Çıktı dosyası oluşturulamadı')
            return jsonify({'error': 'Çıktı dosyası oluşturulamadı'}), 500
        
        logger.info(f'Dönüştürme başarılı: {output_path}')
        
        response = send_file(
            output_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=f'converted.{output_ext}'
        )
        
        @response.call_on_close
        def cleanup():
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
            except Exception as e:
                logger.error(f'Temizlik hatası: {e}')
        
        return response
    
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Dönüştürme zaman aşımına uğradı'}), 504
    except Exception as e:
        logger.error(f'Beklenmeyen hata: {str(e)}')
        return jsonify({'error': 'Sunucu hatası', 'details': str(e)}), 500

@app.route('/convert-to-udf', methods=['POST'])
def convert_to_udf():
    """DOCX/PDF → UDF dönüştürme"""
    try:
        if 'file' not in request.files:
            logger.error('Dosya bulunamadı')
            return jsonify({'error': 'Dosya bulunamadı'}), 400
        
        file = request.files['file']
        
        if not file.filename:
            return jsonify({'error': 'Dosya adı geçersiz'}), 400
        
        # Dosya tipini belirle
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext == 'docx':
            script = 'docx_to_udf.py'
            input_suffix = '.docx'
            mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif file_ext == 'pdf':
            script = 'scanned_pdf_to_udf.py'
            input_suffix = '.pdf'
            mime_type = 'application/pdf'
        else:
            return jsonify({'error': 'Geçersiz dosya tipi (docx veya pdf olmalı)'}), 400
        
        logger.info(f'UDF dönüştürme başlıyor: {file.filename} -> UDF')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=input_suffix) as tmp:
            file.save(tmp.name)
            input_path = tmp.name
        
        result = subprocess.run(
            ['python3', script, input_path],
            capture_output=True,
            text=True,
            timeout=60  # PDF → UDF daha uzun sürebilir
        )
        
        if result.returncode != 0:
            logger.error(f'Script hatası: {result.stderr}')
            return jsonify({'error': 'Dönüştürme başarısız', 'details': result.stderr}), 500
        
        output_path = input_path.replace(input_suffix, '.udf')
        
        if not os.path.exists(output_path):
            logger.error('UDF dosyası oluşturulamadı')
            return jsonify({'error': 'UDF dosyası oluşturulamadı'}), 500
        
        logger.info(f'UDF dönüştürme başarılı: {output_path}')
        
        response = send_file(
            output_path,
            mimetype='application/zip',  # UDF is essentially a ZIP
            as_attachment=True,
            download_name='converted.udf'
        )
        
        @response.call_on_close
        def cleanup():
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
            except Exception as e:
                logger.error(f'Temizlik hatası: {e}')
        
        return response
    
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Dönüştürme zaman aşımına uğradı (60 saniye)'}), 504
    except Exception as e:
        logger.error(f'Beklenmeyen hata: {str(e)}')
        return jsonify({'error': 'Sunucu hatası', 'details': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
