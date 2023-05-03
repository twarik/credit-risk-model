from application import app

if __name__ == "__main__":
    print(
        (
            "*Flask starting server...\n"
            "please wait until server has fully started"
        )
    )
    # start api server
    app.run(debug=False)
