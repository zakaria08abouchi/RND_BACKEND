from rnd_api import app

if __name__ == '__main__':
    app.run(threaded=True, debug=True, host='0.0.0.0', port=5000)
