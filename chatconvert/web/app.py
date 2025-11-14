"""
Flask web application for ChatConvert-Toolkit.

Provides REST API for file conversion and analytics.
"""

import os
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename

from ..engine import ConversionEngine
from ..analytics import AnalyticsEngine


def create_app():
    """Create and configure Flask app."""
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

    # Enable CORS
    CORS(app)

    # Initialize engines
    conversion_engine = ConversionEngine()
    analytics_engine = AnalyticsEngine(use_ai=False)  # Default to keyword-based

    # Allowed extensions
    ALLOWED_EXTENSIONS = set(conversion_engine.list_supported_formats()['input'])

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # Routes
    @app.route('/')
    def index():
        """Serve simple web UI."""
        return render_template_string(HTML_TEMPLATE)

    @app.route('/api/formats', methods=['GET'])
    def get_formats():
        """Get supported formats."""
        formats = conversion_engine.list_supported_formats()
        return jsonify(formats)

    @app.route('/api/convert', methods=['POST'])
    def convert_file():
        """Convert uploaded file to specified format."""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        output_format = request.form.get('format', 'html')

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Unsupported file type'}), 400

        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            input_path = Path(app.config['UPLOAD_FOLDER']) / filename
            file.save(str(input_path))

            # Convert
            output_path = input_path.with_suffix(f'.{output_format}')
            result = conversion_engine.convert(str(input_path), str(output_path), output_format)

            if not result.success:
                return jsonify({'error': result.errors}), 500

            # Send converted file
            return send_file(
                str(output_path),
                as_attachment=True,
                download_name=output_path.name
            )

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Cleanup
            if input_path.exists():
                input_path.unlink()

    @app.route('/api/analyze', methods=['POST'])
    def analyze_file():
        """Analyze uploaded file."""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Unsupported file type'}), 400

        try:
            # Save and parse
            filename = secure_filename(file.filename)
            input_path = Path(app.config['UPLOAD_FOLDER']) / filename
            file.save(str(input_path))

            # Parse conversation
            parser = conversion_engine._get_parser(str(input_path))
            conversation = parser.parse(str(input_path))

            # Analyze
            results = analytics_engine.analyze(conversation)

            return jsonify(results)

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if input_path.exists():
                input_path.unlink()

    return app


# Simple HTML template for the web UI
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>ChatConvert Toolkit</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 { color: #667eea; margin-bottom: 30px; }
        .section { margin-bottom: 30px; }
        h2 { color: #333; margin-bottom: 15px; font-size: 20px; }
        select, input[type="file"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
        }
        button:hover { opacity: 0.9; }
        .result {
            margin-top: 20px;
            padding: 15px;
            background: #f0f0f0;
            border-radius: 5px;
            display: none;
        }
        .error { background: #ffebee; color: #c62828; }
        .success { background: #e8f5e9; color: #2e7d32; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💬 ChatConvert Toolkit</h1>

        <div class="section">
            <h2>Convert Chat File</h2>
            <form id="convertForm">
                <input type="file" id="convertFile" required>
                <select id="outputFormat" required>
                    <option value="html">HTML</option>
                    <option value="md">Markdown</option>
                    <option value="pdf">PDF</option>
                    <option value="docx">DOCX</option>
                    <option value="json">JSON</option>
                    <option value="txt">TXT</option>
                    <option value="db">SQLite</option>
                    <option value="xmind">XMind</option>
                </select>
                <button type="submit">Convert</button>
            </form>
            <div id="convertResult" class="result"></div>
        </div>

        <div class="section">
            <h2>Analyze Chat File</h2>
            <form id="analyzeForm">
                <input type="file" id="analyzeFile" required>
                <button type="submit">Analyze</button>
            </form>
            <div id="analyzeResult" class="result"></div>
        </div>
    </div>

    <script>
        document.getElementById('convertForm').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData();
            formData.append('file', document.getElementById('convertFile').files[0]);
            formData.append('format', document.getElementById('outputFormat').value);

            const result = document.getElementById('convertResult');
            result.style.display = 'block';
            result.innerHTML = 'Converting...';

            try {
                const response = await fetch('/api/convert', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'converted.' + document.getElementById('outputFormat').value;
                    a.click();
                    result.className = 'result success';
                    result.innerHTML = '✓ File converted successfully! Download started.';
                } else {
                    const error = await response.json();
                    result.className = 'result error';
                    result.innerHTML = '✗ Error: ' + (error.error || 'Conversion failed');
                }
            } catch (error) {
                result.className = 'result error';
                result.innerHTML = '✗ Error: ' + error.message;
            }
        };

        document.getElementById('analyzeForm').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData();
            formData.append('file', document.getElementById('analyzeFile').files[0]);

            const result = document.getElementById('analyzeResult');
            result.style.display = 'block';
            result.innerHTML = 'Analyzing...';

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (response.ok) {
                    let html = '<strong>Analysis Results:</strong><br><br>';

                    if (data.sentiment) {
                        html += `<strong>Sentiment:</strong> ${data.sentiment.overall_sentiment} (${data.sentiment.sentiment_score.toFixed(2)})<br>`;
                    }

                    if (data.topics && data.topics.main_topics) {
                        html += `<strong>Topics:</strong> ${data.topics.main_topics.slice(0, 5).join(', ')}<br>`;
                    }

                    if (data.activity) {
                        html += `<strong>Messages:</strong> ${data.activity.total_messages}<br>`;
                        html += `<strong>Most Active:</strong> ${data.activity.most_active_participant.name || 'Unknown'}<br>`;
                    }

                    if (data.word_frequency) {
                        html += `<strong>Words:</strong> ${data.word_frequency.total_words} total, ${data.word_frequency.unique_words} unique<br>`;
                    }

                    result.className = 'result success';
                    result.innerHTML = html;
                } else {
                    result.className = 'result error';
                    result.innerHTML = '✗ Error: ' + (data.error || 'Analysis failed');
                }
            } catch (error) {
                result.className = 'result error';
                result.innerHTML = '✗ Error: ' + error.message;
            }
        };
    </script>
</body>
</html>
'''


if __name__ == '__main__':
    app = create_app()
    print("Starting ChatConvert Toolkit Web Server...")
    print("Access the web interface at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
