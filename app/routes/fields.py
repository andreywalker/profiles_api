from flask import Blueprint, jsonify, request
from .. import db
from ..models import FieldDef, FIELD_TYPES

fields_bp = Blueprint("fields", __name__)


def error(msg, code):
    return jsonify({"error": msg}), code


@fields_bp.get("/")
def list_fields():
    fields = FieldDef.query.order_by(FieldDef.deletable.desc(), FieldDef.position).all()  # Facts last
    return jsonify([f.to_dict() for f in fields]), 200


@fields_bp.get("/<int:field_id>")
def get_field(field_id):
    field = db.session.get(FieldDef, field_id)
    if field is None:
        return error("Field not found", 404)
    return jsonify(field.to_dict()), 200


@fields_bp.post("/")
def create_field():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    ftype = (data.get("type") or "TEXT").upper()
    if not name:
        return error("name is required", 400)
    if ftype not in FIELD_TYPES:
        return error(f"type must be one of {sorted(FIELD_TYPES)}", 400)
    if FieldDef.query.filter_by(name=name).first():
        return error("field already exists", 409)
    position = (db.session.query(db.func.max(FieldDef.position)).scalar() or 0) + 1
    field = FieldDef(name=name, type=ftype, position=position)
    db.session.add(field)
    db.session.commit()
    return jsonify(field.to_dict()), 201


@fields_bp.put("/<int:field_id>")
def update_field(field_id):
    field = db.session.get(FieldDef, field_id)
    if field is None:
        return error("Field not found", 404)
    data = request.get_json(silent=True) or {}
    if "name" in data:
        name = (data["name"] or "").strip()
        if not name:
            return error("name cannot be empty", 400)
        if FieldDef.query.filter(FieldDef.name == name, FieldDef.id != field_id).first():
            return error("field already exists", 409)
        field.name = name
    if "type" in data:
        ftype = (data["type"] or "").upper()
        if ftype not in FIELD_TYPES:
            return error(f"type must be one of {sorted(FIELD_TYPES)}", 400)
        field.type = ftype
    db.session.commit()
    return jsonify(field.to_dict()), 200


@fields_bp.delete("/<int:field_id>")
def delete_field(field_id):
    field = db.session.get(FieldDef, field_id)
    if field is None:
        return error("Field not found", 404)
    if not field.deletable:
        return error(f"'{field.name}' cannot be deleted", 400)
    db.session.delete(field)       # all persons' values for it are deleted too (cascade)
    db.session.commit()
    return jsonify({"message": f"Field {field_id} deleted"}), 200