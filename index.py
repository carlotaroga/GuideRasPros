from flask import Flask, render_template, request, redirect, jsonify, flash, send_file
import os
import tempfile
from werkzeug.utils import secure_filename

from uspekpy import batch_simulation

app = Flask(__name__)

# Allowed extensions
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

EXAMPLES_FOLDER = 'static/resources/'  

# Function to check if the file extension is valid
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/')
def home():
    
    return render_template('home.html')  

@app.route('/batch')
def batch():
    return render_template('batch.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/download_example', methods=['POST'])
def download_example():
    data = request.get_json()
    file_format = data.get('format')
    
    # Check the requested format and assign the corresponding file
    if file_format == 'CSV':
        file_path = os.path.join(EXAMPLES_FOLDER, 'input.csv')
    elif file_format == 'Excel':
        file_path = os.path.join(EXAMPLES_FOLDER, 'input.xlsx')
    else:
        return jsonify({'error': 'Formato no válido'}), 400

    # Check if the file exists
    if not os.path.exists(file_path):
        return jsonify({'error': 'Archivo de ejemplo no encontrado'}), 404
    
    # Send the file to download
    return send_file(file_path, as_attachment=True)

@app.route('/upload_file', methods=['POST'])
def upload_file():
    # Check if the form has a file
    if 'input_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['input_file']
    file_format = request.form.get('file_format') 
    # If no file is selected or the file name is empty
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    # Check if the file has an allowed extension
    if file and allowed_file(file.filename):
        
        filename = secure_filename(file.filename)
   
        # Save the file to the temporary folder
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, filename)
   
        file.save(file_path)
        
        print(file_path)
        flash(f'Archivo subido y guardado en: {file_path}')
        

        # Call the batch_simulation function with the defined input CSV file
        df = batch_simulation(input_file_path=file_path)

        # Define the path of the output file where the simulation results will be saved
        my_output_csv = 'output/%s.%s' % (filename, file_format) 


        # Save results to a CSV file
        df.to_csv(my_output_csv, index=True)

        # Print results
        print(df.to_string())

        return send_file(my_output_csv, as_attachment=True)
    
    
    flash('El archivo no tiene una extensión permitida')
    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)



