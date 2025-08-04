from api import create_app

app = create_app()

# debugger should not be enabled in production
# mac, use port=5001
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
