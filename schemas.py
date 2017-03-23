from marshmallow import ValidationError
from marshmallow import fields, validate, validates
from marshmallow_peewee import ModelSchema
from models import User, Project, Task
from marshmallow_peewee import Related
from flask_login import current_user


class UserSchema(ModelSchema):
    username = fields.Str(validate=[validate.Length(min=3, max=50)], required=True)
    password = fields.Str(validate=[validate.Regexp('[A-Za-z0-9]+')])

    class Meta:
        model = User
        exclude = ["password", "state"]


class ProjectSchema(ModelSchema):
    name = fields.Str(validate=[validate.Length(min=3, max=100)], required=True)
    color = fields.Str(validate=[validate.Regexp('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')], required=True)
    user = Related(nested=UserSchema)

    class Meta:
        model = Project

        # Эта валидация работает и полезна при создании проэкта
        # Но мешает при обновлении
        # Не придумал как организовать чтобы при обновлении
        # проверялось на уникальность кроме обноляемого проекта
        # если можно прокоментируй плиз :)

        # @validates('name')
        # def validate_name(self, value):
        #     if Project.filter(Project.name == value).where(Project.user == current_user.id).exists():
        #         raise ValidationError("Project name {} already exists".format(value))
        #
        # @validates('color')
        # def validate_name(self, value):
        #     if Project.filter(Project.color == value).where(Project.user == current_user.id).exists():
        #         raise ValidationError("Project color {} already taken".format(value))


class TaskSchema(ModelSchema):
    title = fields.Str(validate=[validate.Length(min=3, max=100)], required=True)
    date = fields.Date(required=True)
    priority = fields.Integer(validate=[validate.Regexp('[0-9]+')])
    project = Related(nested=ProjectSchema)

    class Meta:
        model = Task

    @validates('project')
    def validate_project(self, value):
        if not Project.filter(Project.id == value).exists():
            raise ValidationError("Can't find project")


user_schema = UserSchema()
project_schema = ProjectSchema()
task_schema = TaskSchema()
