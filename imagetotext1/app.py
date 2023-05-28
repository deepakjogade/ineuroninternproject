import base64
import os
import werkzeug
from math import floor
import logging
import pytesseract
from PIL import Image
from flask import Flask, render_template, request, Response
from flask_restful import Api, Resource, reqparse


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 


REDUCTION_COEFFICIENT = 0.9
QUALITY = 85

logging.basicConfig(filename='record.log', level=logging.DEBUG)
app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')


@app.route('/')
def getstarted():
    return render_template('getstarted.html')


@app.route('/index/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
    

@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    try:
        image_file = request.files.get('image_file', '')
        # create byte stream from uploaded file
        file = request.files['image_file'].read()  # byte file
        img = Image.open(image_file)
        img1 = img.convert('LA')
        print("Before reducing", img1.size)
        imgsize = len(file) >> 20
        if imgsize > 2:
            x, y = img1.size
            x *= REDUCTION_COEFFICIENT
            y *= REDUCTION_COEFFICIENT
            img1 = img1.resize((floor(x), floor(y)), Image.BICUBIC)
            print("Img reduced", img1.size)
        ext = "jpeg"
        if "." in image_file.filename:
            ext = image_file.filename.rsplit(".", 1)[1]
        text = pytesseract.image_to_string(img1)
        # Base64 encoding the uploaded image
        img_base64 = base64.b64encode(file)
        img_base64_str = str(img_base64)
        # final base64 encoded string
        img_base64_str = "data:image/" + ext + ";base64,"+img_base64_str.split('\'', 1)[1][0:-1]
        f = open("sample.txt", "a")
        f.truncate(0)
        f.write(text)
        f.close()
        return render_template('result.html', var=text, img=img_base64_str)
    except Exception as e:
        print(e) 
        return render_template('error.html')

    
@app.route("/gettext")
def gettext():
    with open("sample.txt") as fp:
        src = fp.read()
        return Response(
            src,
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=sample.txt"})

    
# ----- API -----
class UploadAPI(Resource):
    def get(self):
        print("check passed")
        return {"message": "API For ImageToText"}, 200

    def post(self):
        data = parser.parse_args()
        if data['file'] == "":
            return {'message': 'No file found'}, 400

        photo = data['file']
        if photo:
            photo.save(os.path.join("./static/images/", photo.filename))
            img = Image.open(photo)
            img1 = img.convert("LA")
            text = pytesseract.image_to_string(img1)
            print("check 1 passed")
            os.remove(os.path.join("./static/images/", photo.filename))
            return {"message": text}, 200
        else:
            return {'message': 'Something went wrong'}, 500


api.add_resource(UploadAPI, "/api/v1/")
# End Of API Endpoint

if __name__ == "__main__":
    app.run(debug=True)



    
    
