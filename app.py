from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def predict(neighborhood, room_type, guests):
    return neighborhood + " " + room_type + " " + guests

@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')
    
@app.route('/rec', methods=['POST'])
def recommendation():
    return jsonify({'rec' : predict(request.form['neighborhood'], request.form['room_type'], request.form['guests'])})
    #return jsonify({'rec' : '$110:'})
    
if __name__ == '__main__':
    app.run()