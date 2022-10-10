# AGV Waypoint Server

The Waypoint Server serves as the centralized control unit responsible for translating user commands, distributing tasks, facilitating multiple AGV navigation, and providing users methods to supervise multi-AGV navigation.

The following documentation contains information on how to start developing on the Waypoint Server, how to run the Waypoint Server, and interfacing with the Waypoint Server.

### New vs. Old Waypoint Server Distinction

You may notice there exist two directories `old_waypoint_server` and `new_waypoint_server`. The former refers to the prototype Waypoint Server associated with the (2020 - 2021) AGV Group, the latter is the Waypoint Server prototype associated with the (2021 - 2022) AGV Group. We recommend deleting the `old_waypoint_server` directory as it has thus far been unused by the (2021-2022) group.

## Setting up the Waypoint Server Development Environment

The following instructions you are using either a Linux or Unix based operating system.

If you are using a Windows operating system, I would highly recommend using WSL2 (Windows Subsystem Linux), as that is the development environment I used while devloping the Waypoint Server. Many [tutorials](https://pureinfotech.com/install-windows-subsystem-linux-2-windows-10/) exist online for installing WSL2.

### Install Git

The [documentation](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) is the best place to start for Git! Pick the installation method that corresponds to your operating system family.

### Clone the Waypoint Server Repository Locally

```bash
# navigate to the directory you desire to clone this repository into
git clone https://github.com/APSCL/waypoint_server.git
```

### Create and Setup Development Virtual Environment

Development of the Waypoint Server takes place within a [virtual environment](https://learn.microsoft.com/en-us/microsoft-desktop-optimization-pack/appv-v4/about-virtual-environments). This is to ensure that all dependencies are replicated across all machines used to develop the Waypoint Server

```bash
# creates a virtual environment named: "venv"
python3 -m venv venv
# activate the virtual environment
source ./venv/bin/activate
# copy all dependencies into the virtual environment
pip install -r ./requirements.txt
# close the virtual environment
deactivate venv
```

Additionally, create a file named `.env` to store Waypoint Server globally defined environment variables.

```bash
SECRET_KEY = somesupersecretkey
SQLALCHEMY_DATABASE_URI = sqlite:///server.db
HOST = 127.0.0.1
PORT = 5000
SQLALCHEMY_TRACK_MODIFICATIONS = True
```

Please note that these are the default environment variables to get the Waypoint Server running. If future teams end up heavily modifying the `.env` file, please consider a more secure way of sharing this file between teams.

### Developing/Launching the Waypoint Server

Always ensure that you run the command before you begin any kind of development work:

```bash
# activate the virtual environment
source ./venv/bin/activate
```

From this point, launch the Waypoint Server with the bash command:

```bash
# from the top level directory
python application.py --run_type dev/deploy/test
```

The `dev` argument refers to launching the Waypoint Server with the development configuration environment as seen in the `new_waypoint_server/config.py` file. If the `run_type` argument is not provided, the Waypoint Server will launch with this configuration.

The `deploy` argument refers to launching the Waypoint Server with the deployment configuration environment as seen in the `new_waypoint_server/config.py` file.

The `test` argument refers to launching the Waypoint Server with the testing configuration environment as seen in the `new_waypoint_server/config.py` file. In retrospect, this development environment seems useless, please consider its removal!

### Launching the Waypoint Server with WSL2

This section is dedicated to Waypoint Server developers on WSL2. Prior to running commands to launch the Waypoint Server in the previous section, ensure the following actions have also been completed:

_1) Allow Portforwarding through the Windows Firewall_
In order to allow requests to be routed through your Window's IP to the virtual IP for WSL2, create a new Inbound Rule within the Window's Firewall Advanced Settings Tab. The Inbound Rule should be on the PORT the Waypoint Server is hosted for consistency, allowing ALL inbound traffic.

_2) Create a Portforwarding Rule for WSL2_
Open a powershell terminal with administrator commands and execute the following commands:

```bash
# reset all portfowarding rules
netsh interface portproxy reset
# verify no portfowarding rules exist
netsh interface portproxy show v4tov4
# create a portforwarding rule from Windows port 5000 to WSL2 virtual port 5000
netsh interface portproxy add v4tov4 listenport=5000 listenaddress=* connectport=5000 connectaddress = $($(wsl hostname -I).Trim());
```

Step 1) only ever needs to be completed once, and we found it is best practice to run Step 2) each time we begin development/testing on the Waypoint Server.

From this point, proceed Waypoint Server launch commands as seen in the previous section.

## Interfacing with the Waypoint Server

### Running Waypoint Server Unit Tests

To run unit tests for the Waypoint Server (found in the directory: `new_waypoint_server/app/tests/`), first ensure the bash command:

```bash
export FLASK_APP=app/app
```

has been executed. This command will need to be entered for each new terminal window unless the `FLASK_APP` environment variable is specified in the `~/.profile` file.

All unit tests are then executed with the following command:

```bash
flask test
# this should then genereate an observable output showing print statements and how many testcases passed
```

### Client Side Interface

To perform administrative operations on the Waypoint Server while it is running, utilize the file `new_waypoint_server/waypoint_server_interface.py` either through import or direct copy and paste.

## Waypoint Server Resource References

Provided below are some tutorials and documentation to fill any existing knowledge gaps. Please consider adding more resources for future groups.

- [Flask Tutorial](https://flask.palletsprojects.com/en/2.2.x/tutorial/) Tutorial
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/)
- [Flask-Blueprint Documentation](https://flask.palletsprojects.com/en/2.2.x/blueprints/)
- [Flask-Marshmallow Documentation](https://flask-marshmallow.readthedocs.io/en/latest/)
- [Dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [Marshmallow-Enum Documentation](https://pypi.org/project/marshmallow-enum/)
- [Full Multiple AGV System Report 2021-2022](https://docs.google.com/document/d/1PWzXRaNC-ERTDzknO0ewaxypTz_3unFS2LD6ZZ-UfPw/edit?usp=sharing)

## TODO

- Coordinate Standardization (Adding Waypoint Server Logic to support all AGVs navigating on the same relative x-y ROS generated coordinate plane)

## Contact Information

For any additional questions, contact previous contributors through their emails:

- ethanjohman@gmail.com
