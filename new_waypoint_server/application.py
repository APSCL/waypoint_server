import argparse
import sys

from app.app import create_app
from app.config import ConfigType

parser = argparse.ArgumentParser()
parser.add_argument("--run_type", type=str, required=False)
args = parser.parse_args()

def retrieve_config(args):
    if not args.run_type: 
        return ConfigType.DEVELOPMENT
    config_type_dict = {'dev':ConfigType.DEVELOPMENT, 'deploy':ConfigType.DEPLOYMENT, 'test':ConfigType.TESTING}
    config_type = config_type_dict.get(args.run_type, None)
    if not config_type:
        sys.exit("[ERROR] - select a valid run_type: [dev deploy test] in order to run server")
    return config_type

application = create_app(conf_type=retrieve_config(args))

if __name__ == "__main__":
    application.run(host=application.config["HOST"], port=application.config["PORT"], debug=True)
