import asyncio
from sanic import Sanic
from sanic.request import Request
from sanic.response import json
from asyncpg.exceptions import IntegrityConstraintViolationError
from gino import Gino
from marshmallow import Schema, fields, post_load, ValidationError, validates

app = Sanic()


db = Gino()
CONN_STRING = 'postgresql://postgres:postgres@localhost/gino'


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    nickname = db.Column(db.Unicode(), default='noname', unique=True)


async def setup():
    async with db.with_bind(CONN_STRING):
        # Create tables
        await db.gino.create_all()


async def create_user(params):
    async with db.with_bind(CONN_STRING):
        # Create object, `id` is assigned by database
        user = await User.create(**params)
        print(user.id, user.nickname)  # 1 fantix
        return user


class UserSchema(Schema):
    id = fields.Int()
    nickname = fields.Str(required=True)

    # @post_load
    # def make_user(self, data, **kwargs):
    #     return User(**data)

    @validates('nickname')
    def validate_name(self, value):
        if len(value) < 5:
            raise ValidationError("name short")


@app.route('/users', methods=['POST'])
async def test(request: Request):
    try:
        data, errs = UserSchema().loads(request.body)
        if errs:
            return json({'errors': errs})
        user = await create_user(data)
        return json(user.to_dict())
    except IntegrityConstraintViolationError as e:
        return json({'errors': {'model': e.args}}, status=422)
    except Exception as e:
        return json({'errors': {'general': e.args}}, status=500)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(setup())
    app.run(host='0.0.0.0', port=8000)
