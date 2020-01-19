from resources import simple_app, ora

app = simple_app.app

if __name__ == "__main__":
    try:
        app.run(debug=(simple_app.parms['LOG_LEVEL']) == 10)
    finally:
        ora.disconnect()
