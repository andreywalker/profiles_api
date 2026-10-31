# Profiles app API

Provides backend service and remote data storage for Profiles mobile app. Data is stored in postgresql database on the server and can be retrieved via REST endpoints

## Structure

- **app** package. Source code folder for Flask application
    - **routes** package contains endpoint files, separated by models so that the do not intersect with each other
    - _config.py_ - app level configuration file
    - _models.py_ - file containing models for SQLAlchemy
- **docs** folder with documentation, describing API endpoints
- **postman** folder with postman collection for endpoints
- _wsgi.py_ file that governs gunicorn - web server for flask
- _Dockerfile_ file describing docker container build steps
- _compose.yaml_ file describing containers level configuration for the project, governing Web app and Db parameters and communication
- _requirements_ - requirements, nothing new