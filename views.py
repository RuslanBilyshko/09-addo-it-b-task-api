from decorators import is_auth
from flask import Flask, request, jsonify, g
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from var_dump import var_dump

from models import User, Project, Task, initialize
from schemas import user_schema, project_schema, task_schema

from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'super secret key'
CORS(app=app)

login_manager = LoginManager(app)


@app.before_request
def before_request():
    g.user = current_user


@login_manager.user_loader
def load_user(id):
    return User.get(id=int(id))


# ***************************************
#               User API
# ***************************************

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    user = User.filter(User.username == username).first()

    if user is None:
        return jsonify({"message": "Incorrect password or username", "status": "error"})

    if not user.password.check_password(password):
        return jsonify({"message": "Incorrect password or username", "status": "error"})

    login_user(user)
    return jsonify({"auth": True})


@app.route('/logout')
def logout():
    logout_user()
    return jsonify({"auth": False})


@app.route('/', methods=["GET"])
def index():
    # User.create(
    #     username='test',
    #     password='test'
    # )

    return jsonify({"status": "ok"})


# *****************************************
#               Task API
# *****************************************
@app.route('/api/task', methods=['GET'])
@is_auth
def task_list():
    return jsonify(task_schema.dump(list(Task.get_list(current_user.id)), many=True).data)


@app.route('/api/task', methods=['POST'])
@is_auth
def task_create():
    task, errors = task_schema.load(request.json)

    if errors:
        return jsonify(errors), 400

    task.save()

    return jsonify(task_schema.dump(task).data), 201


@app.route('/api/task/<int:task_id>', methods=['GET'])
@is_auth
def task_edit(task_id):
    task = Task.get_item(task_id, current_user.id)

    if not task:
        return jsonify({"message": "Can't find task with id - `{id}`".format(id=task_id), "status": "error"}), 404

    return jsonify(task_schema.dump(task, many=True).data)


@app.route('/api/task/<int:task_id>', methods=['PUT'])
@is_auth
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
@is_auth
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
@is_auth
def project_list():
    return jsonify(project_schema.dump(list(Project.get_list(current_user.id)), many=True).data)


@app.route('/api/project', methods=['POST'])
@is_auth
def project_create():
    project, errors = project_schema.load(request.json)

    if errors:
        return jsonify(errors), 400

    project.user = current_user.id
    project.save()

    return jsonify(project_schema.dump(project).data), 201


@app.route('/api/project/<int:project_id>', methods=['PUT'])
@is_auth
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
@is_auth
def project_delete(project_id):
    try:
        project = Project.get(id=project_id, user=current_user.id)
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

    return jsonify({"message": "The project has been successfully deleted", "status": "success"}), 410


if __name__ == '__main__':
    initialize()
    # app.debug = True
    # app.run()
    app.run(use_reloader=True)
