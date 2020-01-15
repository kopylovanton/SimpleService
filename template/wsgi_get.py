from resources import app, parms, ora


if __name__ == "__main__":
        try:
                app.run(debug=(parms['LOG_LEVEL']) == 10)
        finally:
                ora.disconnect()
