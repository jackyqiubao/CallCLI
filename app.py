from flask import Flask, request, jsonify
import os
import subprocess
cli_path = '/Users/jackyqiu/Code/PicturesTo3D/CLI/CreatingAPhotogrammetryCommandLineApp/DerivedData/HelloPhotogrammetry/Build/Products/Debug/HelloPhotogrammetry'
app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    folder_name = request.form.get('folder_name')
    completed = request.form.get('completed', 'false').lower() == 'true'
    file = request.files.get('image')

    if not folder_name or not file:
        return jsonify({'error': 'Missing parameters: folder_name and image are required'}), 400

    base_dir = os.getcwd()  # /Users/jackyqiu/Code/PicturesTo3D/CallCLI
    folder_path = os.path.join(base_dir, folder_name)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    pics_path = os.path.join(folder_path, 'pics')
    if not os.path.exists(pics_path):
        os.makedirs(pics_path)

    file_path = os.path.join(pics_path, file.filename)
    file.save(file_path)

    if completed:
        output_dir = os.path.join(folder_path, '3doutput')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_filename = os.path.join(output_dir, '3dresult.usdz')
        try:
            result = subprocess.run([cli_path,"--input-folder", pics_path,"--output-filename", output_filename], capture_output=True, text=True)
            if result.returncode != 0:
                return jsonify({'error': f'CLI failed: {result.stderr}'}), 500
        except Exception as e:
            return jsonify({'error': f'Failed to run CLI: {str(e)}'}), 500

    return jsonify({'message': 'Image uploaded successfully', 'completed': completed})

if __name__ == '__main__':
    app.run(debug=True)