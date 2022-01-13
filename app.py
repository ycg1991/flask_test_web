from flask import Flask
import config
from iteration_version import iteration_version
from user import user
from iteration_manage import iteration
from iteration_records import iteration_records
from system_manage import system
from feedback_record import feedback
app = Flask(__name__)
app.config.from_object(config)
# 注册蓝图到app
app.register_blueprint(user)
app.register_blueprint(iteration)
app.register_blueprint(iteration_version)
app.register_blueprint(iteration_records)
app.register_blueprint(system)
app.register_blueprint(feedback)

if __name__ == '__main__':
    app.run(debug=True, host='10.7.52.79', port=5000)
