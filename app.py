from backend import create_app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        print("Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])
    app.run(debug=True)

# mahmoud elqalini
# mahmoud ramadan
# habiba abdelmalik