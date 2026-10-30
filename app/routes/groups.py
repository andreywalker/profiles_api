from flask import Blueprint, jsonify, request
from .. import db
from ..models import Group, Person

groups_bp = Blueprint("groups", __name__)


def error(msg, code):
    return jsonify({"error": msg}), code


@groups_bp.get("/")
def list_groups():
    groups = Group.query.order_by(Group.is_default, Group.name).all()   # "No group" last
    return jsonify([g.to_dict() for g in groups]), 200


@groups_bp.get("/<int:group_id>")
def get_group(group_id):
    group = db.session.get(Group, group_id)
    if group is None:
        return error("Group not found", 404)
    result = group.to_dict()
    result["persons"] = [{"id": p.id, "name": f"{p.first_name} {p.surname}"}
                         for p in group.persons]
    return jsonify(result), 200


@groups_bp.post("/")
def create_group():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return error("name is required", 400)
    if Group.query.filter_by(name=name).first():
        return error("group already exists", 409)
    group = Group(name=name)
    db.session.add(group)
    db.session.commit()
    return jsonify(group.to_dict()), 201


@groups_bp.put("/<int:group_id>")
def rename_group(group_id):
    group = db.session.get(Group, group_id)
    if group is None:
        return error("Group not found", 404)
    if group.is_default:
        return error("'No group' cannot be changed", 400)
    name = ((request.get_json(silent=True) or {}).get("name") or "").strip()
    if not name:
        return error("name is required", 400)
    if Group.query.filter(Group.name == name, Group.id != group_id).first():
        return error("group already exists", 409)
    group.name = name
    db.session.commit()
    return jsonify(group.to_dict()), 200


@groups_bp.delete("/<int:group_id>")
def delete_group(group_id):
    group = db.session.get(Group, group_id)
    if group is None:
        return error("Group not found", 404)
    if group.is_default:
        return error("'No group' cannot be deleted", 400)
    default = Group.query.filter_by(is_default=True).first()
    Person.query.filter_by(group_id=group_id).update({"group_id": default.id})
    db.session.delete(group)
    db.session.commit()            # both steps in one transaction
    return jsonify({"message": f"Group {group_id} deleted, its persons moved to 'No group'"}), 200