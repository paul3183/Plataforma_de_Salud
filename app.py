
import os
import requests
from dotenv import load_dotenv
from fpdf import FPDF
from flask import Flask, request, send_file, render_template

# Carga las variables de entorno desde un archivo .env
load_dotenv()

# Configuración de la clave de API y el endpoint de la API de OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

# Configuración de encabezados
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {OPENAI_API_KEY}'
}

app = Flask(__name__)

@app.route('/')
def index():
    # Renderizar la plantilla del formulario HTML
    return render_template('form_salud.html')

@app.route('/form_salud', methods=['POST'])
def form_salud():
    # Captura los datos del formulario
    nombre = request.form['nombre']
    edad = request.form['edad']
    peso = request.form['peso']
    altura = request.form['altura']
    glucosa = request.form['glucosa']
    presion_sistolica = request.form['presion_sistolica']
    presion_diastolica = request.form['presion_diastolica']
    alergias = request.form['alergias']
    actividad_fisica = request.form['actividad_fisica']
    sintomas = request.form.get('sintomas', 'No especificado')
    historial = request.form.get('historial', 'No especificado')
    alimentacion = request.form.get('alimentacion', 'No especificado')
    vacunacion = request.form.get('vacunacion', 'No especificado')
    medicaciones = request.form.get('medicaciones', 'No especificado')

    # Generar el prompt para OpenAI
    prompt = f"Informe de salud para {nombre}, de {edad} años, con un peso de {peso} kg y una altura de {altura} cm. El nivel de glucosa en sangre es de {glucosa} mg/dL. La presión arterial es de {presion_sistolica}/{presion_diastolica} mmHg. Síntomas: {sintomas}. Alergias: {alergias}. Nivel de actividad física: {actividad_fisica}. Historial médico familiar: {historial}. Hábitos alimenticios: {alimentacion}. Historial de vacunación: {vacunacion}. Medicaciones actuales: {medicaciones}., este informe no debe ser enumerado, mas bien una narración como tal, y que pueda ser un informe , recuerda eres un health full assistant"

    # Datos que se enviarán en la solicitud POST
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 1000,
        'temperature': 0.7
    }

    # Realizar la solicitud POST a la API de OpenAI
    respuesta = requests.post(OPENAI_API_URL, headers=headers, json=data)
    if respuesta.status_code == 200:
        respuesta_texto = respuesta.json()['choices'][0]['message']['content'].strip()
    else:
        respuesta_texto = "No se pudo obtener una respuesta de OpenAI."

    # Crear el PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_title("Informe de Salud")
    # Organizar la información del formulario en el PDF
    pdf.multi_cell(0, 10, txt=f"Informe de Salud Preventiva\n\nNombre: {nombre}\nEdad: {edad}\nPeso: {peso} kg\nAltura: {altura} cm\nGlucosa: {glucosa} mg/dL\nPresion_sistolica: {presion_sistolica} mmHg\nPresion_diastolica: {presion_diastolica} mmHg\nAlergias: {alergias}\nActividad_fisica: {actividad_fisica}\nSintomas: {sintomas}\nHistorial: {historial}\n", align='L')

    # Añadir el informe generado por OpenAI
    pdf.multi_cell(0, 10, txt=f"Informe Médico:\n{respuesta_texto}")
    
    # Guardar el PDF
    pdf_output = 'Informe_Salud.pdf'
    pdf.output(pdf_output)

    # Enviar el PDF al usuario
    return send_file(pdf_output, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True, host='0.0.0.0')
