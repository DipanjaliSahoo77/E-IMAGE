from flask import Flask, render_template, request, flash # type: ignore
from werkzeug.utils import secure_filename # type: ignore
import os
import cv2
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'  # Required for flashing messages

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation):
    img = cv2.imread(f"uploads/{filename}")
    if img is None:
        return None  # Handle invalid image files

    newFilename = None

    if operation == "cgray":
        imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        newFilename = f"static/{filename}"
        cv2.imwrite(newFilename, imgProcessed)
    elif operation == "cwebp":
        newFilename = f"static/{filename.split('.')[0]}.webp"
        cv2.imwrite(newFilename, img)
    elif operation == "cjpg":
        newFilename = f"static/{filename.split('.')[0]}.jpg"
        cv2.imwrite(newFilename, img)
    elif operation == "cpng":
        newFilename = f"static/{filename.split('.')[0]}.png"
        cv2.imwrite(newFilename, img)
    else:
        return None  # Handle unsupported operations

    return newFilename


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get('operation')  # Correct usage of get
        
        # Check if the request contains a file
        if 'file' not in request.files:
            flash('No file part in the request.')
            return render_template("index.html", error="No file part in the request.")
        
        file = request.files['file']
        
        # Check if the user has selected a file
        if file.filename == '':
            flash('No file selected.')
            return render_template("index.html", error="No file selected.")
        
        # Validate the file type and save it
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Process the uploaded image
            new=processImage(filename, operation)
            flash(f"Your image has been processed and is available <a href='/{new}' target='_blank'>here</a>.")
            return render_template("index.html")
        
        # Invalid file type
        flash('Invalid file type. Allowed types: png, webp, jpg, jpeg, gif.')
        return render_template("index.html", error="Invalid file type.")
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)