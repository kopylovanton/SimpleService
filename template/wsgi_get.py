# ************* Import
from resources.service_get import app, ora, parms


if __name__ == "__main__":
    try:
        app.run(debug=(parms['LOG_LEVEL']) == 10)
    finally:
        ora.disconnect()