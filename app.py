from flask import Flask, request, render_template
import os
from single_parser import ResumeParser

app = Flask(__name__, template_folder='templates')

# Set the upload folder and allowed extensions
UPLOAD_FOLDER = 'Resumes/'
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if 'file' not in request.files:
            return render_template("upload.html", output={"error": "No file part"})
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template("upload.html", output={"error": "No selected file"})

        if file and allowed_file(file.filename):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            details = ResumeParser.parse_resume(filepath)

            # Return the upload page with parsed details
            return render_template("upload.html", output=details)

        return render_template("upload.html", output={"error": "File type not allowed"})
    
    # If GET request, render the upload page
    return render_template("upload.html", output=None)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
