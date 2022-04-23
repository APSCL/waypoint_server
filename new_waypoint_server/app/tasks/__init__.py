from flask import Blueprint                            
from flask_restful import Api
                                                       
tasks = Blueprint('tasks', __name__) 
tasks_api = Api(tasks)  
                                                                                     
from . import views 