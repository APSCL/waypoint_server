from flask import Blueprint                            
from flask_restful import Api
                                                       
agvs = Blueprint('agvs', __name__) 
agvs_api = Api(agvs)  
                                                                                     
from . import views
