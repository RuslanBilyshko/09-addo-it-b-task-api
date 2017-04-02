import peewee as pw
from playhouse.fields import PasswordField
from datetime import date

db = pw.SqliteDatabase('database.db')


def initialize():
    User.create_table(fail_silently=True)
    Project.create_table(fail_silently=True)
    Task.create_table(fail_silently=True)

    try:

        User.create(
            id=1,
            username='root',
            password='123'
        )


    except pw.IntegrityError:
        pass


class BaseModel(pw.Model):
    class Meta:
        database = db


class User(BaseModel):
    username = pw.CharField(max_length=70, unique=True)
    password = PasswordField()
    state = pw.BooleanField(default=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.state

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)


class Project(BaseModel):
    name = pw.CharField(max_length=100)
    color = pw.CharField(max_length=100)
    user = pw.ForeignKeyField(User)

    @classmethod
    def get_item(cls, project_id, current_user_id):
        return Project.select().where(Project.id == project_id, Project.user == current_user_id)

    @classmethod
    def get_list(cls, current_user_id):
        return Project.select().where(Project.user == current_user_id)


class Task(BaseModel):
    title = pw.CharField(max_length=100)
    date = pw.DateField()
    priority = pw.IntegerField(default=0)
    project = pw.ForeignKeyField(Project)

    # Получение задачи с фильтрацией на текущего пользователя
    @classmethod
    def get_item(cls, task_id, current_user_id):
        return Task.select() \
            .where(Task.id == task_id) \
            .join(Project) \
            .where(Project.user == current_user_id)

    # Получение списка задач с фильтрацией на текущего пользователя
    @classmethod
    def get_list(cls, current_user_id):
        return Task.select() \
            .join(Project) \
            .where(Project.user == current_user_id)
