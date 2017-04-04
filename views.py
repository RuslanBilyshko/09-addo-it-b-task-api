from flask import Flask, request, jsonify, g
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from var_dump import var_dump

from models import User, Project, Task, initialize
from schemas import user_schema, project_schema, task_schema
from flask_cors import CORS
from flask.ext.jwt import JWT, jwt_required, current_identity

app = Flask(__name__)
app.secret_key = 'super secret key'
CORS(app=app)

app.config['JWT_AUTH_URL_RULE'] = '/login'


def authenticate(username, password):
    user = User.filter(User.username == username).first()
    if user and user.password.check_password(password):
        return user

    return None


def identity(payload):
    user_id = payload['identity']
    try:
        return User.get(id=user_id)
    except User.DoesNotExist:
        return None


jwt = JWT(app, authenticate, identity)


@app.before_request
def before_request():
    g.user = current_identity


# ***************************************
#               User API
# ***************************************

@app.route('/logout')
def logout():
    logout_user()
    return jsonify({"auth": False})


@app.route('/', methods=["GET"])
def index():
    # Project.create(
    #     name="Project Job 1",
    #     color="#f8f8f8",
    #     user = 1
    # )

    # Project.create(
    #     name="Project Job 2",
    #     color="#f8f8f8",
    #     user=1
    # )
    #
    # Project.create(
    #     name="Project Job 3",
    #     color="#808080",
    #     user=1
    # )
    #
    # Project.create(
    #     name="Project Job 4",
    #     color="#C0C0C0",
    #     user=1
    # )
    #
    # Project.create(
    #     name="Project Job 2",
    #     color="#f8f8f8",
    #     user=1
    # )
    #
    # Project.create(
    #     name="Project Job 3",
    #     color="#808080",
    #     user=1
    # )
    #
    # Project.create(
    #     name="Project Job 4",
    #     color="#C0C0C0",
    #     user=1
    # )

    # Task.create(
    #     title="Test Task 1",
    #     date="2017-04-20",
    #     project=1,
    #
    # )
    #
    # Task.create(
    #     title="Test Task 2",
    #     date="2017-04-25",
    #     project=1
    # )
    #
    # Task.create(
    #     title="Test Task 3",
    #     date="2017-05-04",
    #     project=2
    # )
    #
    # Task.create(
    #     title="Test Task 4",
    #     date="2017-06-20",
    #     project=2
    # )

    return jsonify({"status": "OK"})


# *****************************************
#               Task API
# *****************************************
@app.route('/api/task', methods=['GET'])
def task_list():
    # return jsonify(task_schema.dump(list(Task.get_list(current_user.id)), many=True).data)

    # Используйте следующие параметры для фильтрации
    # project, priority, date, date_lte, date_gte
    # Для указания страницы - page

    params = request.args.to_dict()
    page = 1
    paginate_by = 1

    if params:

        ordered = None

        if 'order_by' in params.keys():
            ordered = params.pop('order_by')

        if 'page' in params.keys():
            page = params.pop('page')

        tasks = Task.filter(**params).paginate(page=int(page), paginate_by=paginate_by)

        if ordered:
            tasks = tasks.order_by(ordered)

        print(tasks)
        tasks = tasks
    else:
        tasks = Task.select().paginate(page=page, paginate_by=paginate_by)

    return jsonify(task_schema.dump(list(tasks), many=True).data)


@app.route('/api/task', methods=['POST'])
def task_create():
    task, errors = task_schema.load(request.json)

    if errors:
        return jsonify(errors), 400

    task.save()

    return jsonify(task_schema.dump(task).data), 201


@app.route('/api/task/<int:task_id>', methods=['GET'])
def task_edit(task_id):
    task = Task.get_item(task_id, current_user.id)

    if not task:
        return jsonify({"message": "Can't find task with id - `{id}`".format(id=task_id), "status": "error"}), 404

    return jsonify(task_schema.dump(task, many=True).data)


@app.route('/api/task/<int:task_id>', methods=['PUT'])
def task_update(task_id):
    task = Task.get_item(task_id, current_user.id)

    if not task:
        return jsonify({"message": "Can't find task with id - `{id}`".format(id=task_id), "status": "error"}), 404

    task, errors = task_schema.load(request.json)
    if errors:
        return jsonify(errors), 400

    task.id = task_id
    task.save()

    return jsonify(task_schema.dump(task).data), 201


@app.route('/api/task/<int:task_id>', methods=['DELETE'])
def task_delete(task_id):
    task = Task.get_item(task_id, current_user.id)

    if not task:
        return jsonify({"message": "Can't find task with id - `{id}`".format(id=task_id), "status": "error"}), 404

    Task.delete().where(Task.id == task_id).execute()

    return jsonify({"message": "The task has been successfully deleted", "status": "success"}), 410


# *****************************************
#               Project API
# ****************************************
@app.route('/api/project', methods=['GET'])
def project_list():
    return jsonify(project_schema.dump(list(Project.select()), many=True).data)
    # return jsonify(project_schema.dump(list(Project.get_list(current_user.id)), many=True).data)


@app.route('/api/project', methods=['POST'])
def project_create():
    project, errors = project_schema.load(request.json)

    if errors:
        return jsonify(errors), 400

    project.user = current_user.id
    project.save()

    return jsonify(project_schema.dump(project).data), 201


@app.route('/api/project/<int:project_id>', methods=['PUT'])
def project_update(project_id):
    try:
        project = Project.get(id=project_id, user=current_user.id)
    except Project.DoesNotExist:
        return jsonify({"message": "Can't find project with id - `{id}`".format(id=project_id), "status": "error"}), 404

    project, errors = project_schema.load(request.json, instance=project)

    if errors:
        return jsonify(errors), 400

    project.save()

    return jsonify(project_schema.dump(project).data), 201


@app.route('/api/project/<int:project_id>', methods=['DELETE'])
def project_delete(project_id):
    try:
        pass
        # project = Project.get(id=project_id, user=current_user.id)
    except Project.DoesNotExist:
        return jsonify({
            "message": "Can't find project with id - `{id}`".format(id=project_id),
            "status": "error"}), 404

    task_relation_count = Task.select().join(Project).where(Project.id == project_id).count()

    if task_relation_count > 0:
        return jsonify({
            "message": "Deletion is not possible. The project is connected with tasks",
            "status": "error"}), 403

    Project.delete().where(Project.id == project_id).execute()

    # return jsonify({"message": "The project has been successfully deleted", "status": "success"}), 201
    return jsonify({"id": project_id}), 201


if __name__ == '__main__':
    initialize()
    # app.debug = True
    # app.run()
    app.run(use_reloader=True)
