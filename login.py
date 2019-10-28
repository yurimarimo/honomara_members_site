from flask_login import LoginManager, UserMixin
from honomara_members_site import app
from collections import defaultdict

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))


class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password


users = {
    1: User(1, "honomara", "honomara"),
    2: User(2, "admin", "admin")
}


nested_dict = lambda: defaultdict(nested_dict)
user_check = nested_dict()
for i in users.values():
    user_check[i.name]["password"] = i.password
    user_check[i.name]["id"] = i.id
