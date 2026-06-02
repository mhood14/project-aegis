from aegis_app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host=app.config["FLASK_RUN_HOST"], port=8000, debug=app.config["FLASK_DEBUG"])
