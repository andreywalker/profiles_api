from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()


def seed():
    from .models import Group, FieldDef
    if Group.query.filter_by(is_default=True).first() is None:
        db.session.add(Group(name="No group", is_default=True))
    if FieldDef.query.count() == 0:
        db.session.add_all([
            FieldDef(name="Favorite color", position=1),
            FieldDef(name="Wishlist", position=2),
            FieldDef(name="Facts", position=3, deletable=False),
        ])
    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from .routes.persons import persons_bp
    from .routes.groups import groups_bp
    from .routes.fields import fields_bp
    app.register_blueprint(persons_bp, url_prefix="/api/persons")
    app.register_blueprint(groups_bp, url_prefix="/api/groups")
    app.register_blueprint(fields_bp, url_prefix="/api/fields")

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    with app.app_context():
        db.create_all()   # create tables if missing
        seed()            # "No group" + 3 built-in fields

    return app