from flask import Flask, jsonify, request
from peewee import *
from marshmallow import Schema, fields, post_load, ValidationError, validates
from datetime import date

db = SqliteDatabase('people.db')


class Person(Model):
    name = CharField(unique=True)
    birthday = DateField()

    class Meta:
        database = db  # This model uses the "people.db" database.


class PersonSchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)
    birthday = fields.Date()

    @post_load
    def make_person(self, data, **kwargs):
        return Person(**data)

    @validates('name')
    def validate_name(self, value):
        if len(value) < 5:
            raise ValidationError("name short")


app = Flask(__name__)


@app.route("/", methods=['POST'])
def create_person():
    try:
        schema = PersonSchema()
        data, errors = schema.load(request.json)
        if errors:
            return jsonify({'errors': errors})
        data.save()
        return schema.dump(data)
    except IntegrityError as e:

        return jsonify({'errors': {'model': e.args}})


def main():
    db.connect()
    db.create_tables([Person])
    app.run(debug=True)


if __name__ == '__main__':
    main()
