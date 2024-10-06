import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'  # Passen Sie dies an Ihre Datenbankeinstellungen an
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Fügen Sie hier weitere Konfigurationsoptionen hinzu