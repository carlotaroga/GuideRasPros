from flask import Flask, render_template, request, redirect, jsonify, flash, send_file
import os
import tempfile
from werkzeug.utils import secure_filename

from uspekpy import batch_simulation

app = Flask(__name__)

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

# Ruta de ejemplo de archivos descargables
EXAMPLES_FOLDER = 'static/resources/'  # Ajusta según tu estructura

# Función para verificar si la extensión del archivo es válida
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
    
    # Verificar el formato solicitado y asignar el archivo correspondiente
    if file_format == 'CSV':
        file_path = os.path.join(EXAMPLES_FOLDER, 'input.csv')
    elif file_format == 'Excel':
        file_path = os.path.join(EXAMPLES_FOLDER, 'input.xlsx')
    else:
        return jsonify({'error': 'Formato no válido'}), 400

    # Verificar si el archivo existe
    if not os.path.exists(file_path):
        return jsonify({'error': 'Archivo de ejemplo no encontrado'}), 404
    
    # Enviar el archivo para descargar
    return send_file(file_path, as_attachment=True)

@app.route('/upload_file', methods=['POST'])
def upload_file():
    # Comprobar si el formulario tiene un archivo
    if 'input_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['input_file']
    file_format = request.form.get('file_format') 
    # si no se selecciono un archivo o el nombre del archivo está vacío
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    # Comprobar si el archivo tiene una extension permitida
    if file and allowed_file(file.filename):
        # Asegurar el nombre del archivo
        filename = secure_filename(file.filename)
   
        # Guardar el archivo en la carpeta temporal
        # Crear una carpeta temporal para almacenar el archivo
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, filename)
   
        # Guardar el archivo en la carpeta temporal
        file.save(file_path)
        
        print(file_path)
        flash(f'Archivo subido y guardado en: {file_path}')
        
        
        #file_path = os.path.join("./data", filename)


        # Define the path to the input CSV file
        #my_csv = 'data/input.csv'

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



