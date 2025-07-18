from flask import Flask, render_template, request
from werkzeug.datastructures import FileStorage
from comprobante_fiscal_sat import ComprobanteFiscal


app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/action/xml", methods=["POST"])
def action_xml():
    file: FileStorage = None
    for file in request.files:
        file = request.files[file]

    comprobante = ComprobanteFiscal.convertirxml(xml=file.stream.read().decode("utf-8"))

    if comprobante is None:
        return {
            "error": True,
            "message": "No es una XML valido"
        }

    return {
        "error": False,
        "message": comprobante.asdict()
    }

app.run(
    host="0.0.0.0",
    port=5000,
    debug=True
)