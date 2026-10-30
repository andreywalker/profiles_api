from datetime import date
from flask import Blueprint, jsonify, request
from .. import db
from ..models import Person, Group, FieldDef, FieldValue

persons_bp = Blueprint("persons", __name__)

GENERAL = ["first_name", "surname", "group_id", "met", "subtitle",
           "phone", "telegram", "instagram", "other_media"]
REQUIRED = ["first_name", "surname", "birth_date"]


def error(msg, code):
    return jsonify({"error": msg}), code


def check_type(field, value):
    """Return True if value fits the custom field's type."""
    try:
        if field.type == "NUMBER":
            float(value)
        elif field.type == "DATE":
            date.fromisoformat(str(value))
        elif field.type == "BOOLEAN":
            return str(value).lower() in ("true", "false")
        return True
    except ValueError:
        return False


def apply_data(person, data):
    """Copy general + custom fields from JSON onto person. Returns an error text or None."""
    for f in GENERAL:
        if f in data:
            setattr(person, f, data[f])

    if "birth_date" in data:
        try:
            person.birth_date = date.fromisoformat(data["birth_date"])
        except (TypeError, ValueError):
            return "birth_date must be YYYY-MM-DD"

    if "group_id" in data and db.session.get(Group, data["group_id"]) is None:
        return "group not found"

    for name, value in (data.get("custom_fields") or {}).items():
        field = FieldDef.query.filter_by(name=name).first()
        if field is None:
            return f"unknown custom field: {name}"
        existing = next((v for v in person.values if v.field is field), None)
        if value is None or value == "":          # empty = remove the value
            if existing:
                person.values.remove(existing)
            continue
        if not check_type(field, value):
            return f"'{name}' must be of type {field.type}"
        if existing:
            existing.value = str(value)
        else:
            person.values.append(FieldValue(field=field, value=str(value)))
    return None


@persons_bp.get("/")
def list_persons():
    query = Person.query
    group_id = request.args.get("group_id", type=int)
    search = request.args.get("search")
    if group_id:
        query = query.filter_by(group_id=group_id)
    if search:
        query = query.filter(Person.first_name.ilike(f"%{search}%")
                             | Person.surname.ilike(f"%{search}%"))
    persons = query.order_by(Person.first_name).all()
    return jsonify([p.to_dict() for p in persons]), 200


@persons_bp.get("/<int:person_id>")
def get_person(person_id):
    person = db.session.get(Person, person_id)
    if person is None:
        return error("Person not found", 404)
    return jsonify(person.to_dict()), 200


@persons_bp.post("/")
def create_person():
    data = request.get_json(silent=True)
    if data is None:
        return error("Invalid JSON", 400)
    missing = [f for f in REQUIRED if not data.get(f)]
    if missing:
        return error(f"missing required fields: {', '.join(missing)}", 400)

    person = Person(group_id=Group.query.filter_by(is_default=True).first().id)
    msg = apply_data(person, data)
    if msg:
        db.session.rollback()
        return error(msg, 400)
    db.session.add(person)
    db.session.commit()
    return jsonify(person.to_dict()), 201


@persons_bp.put("/<int:person_id>")
def update_person(person_id):
    person = db.session.get(Person, person_id)
    if person is None:
        return error("Person not found", 404)
    data = request.get_json(silent=True)
    if data is None:
        return error("Invalid JSON", 400)
    msg = apply_data(person, data)
    if msg:
        db.session.rollback()
        return error(msg, 400)
    db.session.commit()
    return jsonify(person.to_dict()), 200


@persons_bp.delete("/<int:person_id>")
def delete_person(person_id):
    person = db.session.get(Person, person_id)
    if person is None:
        return error("Person not found", 404)
    db.session.delete(person)          # its custom values are deleted too (cascade)
    db.session.commit()
    return jsonify({"message": f"Person {person_id} deleted"}), 200