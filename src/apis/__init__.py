from flask_restx import Api

from .admin import api as admin_api
from .data import api as data_api
from .dives import api as dives_api
from .feedback import api as feedback_api
from .healthcheck import api as healthcheck_api
from .login import api as login_api
from .register import api as register_api
from .targets import api as targets_api
from .test import api as test_api
from .testadmin import api as testadmin_api
from .users import api as users_api

api = Api(
    title='Api for diving notifications'
)

api.add_namespace(admin_api, path='/api/admin')
api.add_namespace(data_api, path='/api/data')
api.add_namespace(dives_api, path='/api/dives')
api.add_namespace(feedback_api, path='/api/feedback')
api.add_namespace(healthcheck_api, path='/api/healthcheck')
api.add_namespace(login_api, path='/api/login')
api.add_namespace(register_api, path='/api/register')
api.add_namespace(targets_api, path='/api/targets')
api.add_namespace(test_api, path='/api/test')
api.add_namespace(testadmin_api, path='/api/testadmin')
api.add_namespace(users_api, path='/api/users')
