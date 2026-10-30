from datetime import date
from . import db

FIELD_TYPES = {"TEXT", "NUMBER", "DATE", "BOOLEAN"}


class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    is_default = db.Column(db.Boolean, nullable=False, default=False)   # "No group"
    persons = db.relationship("Person", back_populates="group")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "is_default": self.is_default,
                "person_count": len(self.persons)}


class Person(db.Model):
    __tablename__ = "persons"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    met = db.Column(db.Text)
    subtitle = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    telegram = db.Column(db.String(100))
    instagram = db.Column(db.String(100))
    other_media = db.Column(db.String(300))

    group = db.relationship("Group", back_populates="persons")
    values = db.relationship("FieldValue", back_populates="person",
                             cascade="all, delete-orphan")

    def age(self):
        today = date.today()
        b = self.birth_date
        return today.year - b.year - ((today.month, today.day) < (b.month, b.day))

    def to_dict(self):
        ordered = sorted(self.values, key=lambda v: (not v.field.deletable, v.field.position))
        return {
            "id": self.id, "first_name": self.first_name, "surname": self.surname,
            "birth_date": self.birth_date.isoformat(), "age": self.age(),
            "group": {"id": self.group.id, "name": self.group.name},
            "met": self.met, "subtitle": self.subtitle, "phone": self.phone,
            "telegram": self.telegram, "instagram": self.instagram,
            "other_media": self.other_media,
            "custom_fields": {v.field.name: v.value for v in ordered},
        }


class FieldDef(db.Model):
    __tablename__ = "field_defs"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False, default="TEXT")
    deletable = db.Column(db.Boolean, nullable=False, default=True)   # Facts = False
    position = db.Column(db.Integer, nullable=False, default=0)
    values = db.relationship("FieldValue", back_populates="field",
                             cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "type": self.type,
                "deletable": self.deletable, "position": self.position}


class FieldValue(db.Model):
    __tablename__ = "field_values"
    person_id = db.Column(db.Integer, db.ForeignKey("persons.id"), primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey("field_defs.id"), primary_key=True)
    value = db.Column(db.Text, nullable=False)
    person = db.relationship("Person", back_populates="values")
    field = db.relationship("FieldDef", back_populates="values")