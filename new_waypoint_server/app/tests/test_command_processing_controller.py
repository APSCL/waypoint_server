from app.agv_request_handlers.controllers import CommandProcessingController
from app.agvs.constants import AGVState
from app.app import create_app
from app.commands.constants import CommandTypes
from app.commands.models import Command
from app.config import ConfigType
from app.database import db
from app.tasks.constants import TaskStatus
from app.tests.utils import create_agv, create_command, create_task
from flask_testing import TestCase


class TestCommandProcessingController(TestCase):
    def create_app(self):
        return create_app(ConfigType.TESTING)

    def _create_set_of_commands(self, agv, task):
        # create two stop commands
        self.stop_command = {
            "agv_id": agv.id,
            "type": CommandTypes.STOP_AGV,
        }
        # create two start commands
        self.start_command = {
            "agv_id": agv.id,
            "type": CommandTypes.START_AGV,
        }

        # create two agv (one relavent one not) commands
        self.relavent_agv_command = {
            "agv_id": agv.id,
            "type": CommandTypes.CANCEL_AGV,
        }
        self.irrelavent_agv_command = {
            "agv_id": -1,
            "type": CommandTypes.START_AGV,
        }
        # create two task cancel (one relavent one not) commands
        self.relavent_task_command = {
            "task_id": task.id,
            "type": CommandTypes.CANCEL_TASK,
        }
        self.irrelavent_task_command = {
            "task_id": -1,
            "type": CommandTypes.CANCEL_TASK,
        }
        [
            create_command(**kwargs)
            for kwargs in [
                self.stop_command,
                self.stop_command,
                self.start_command,
                self.start_command,
                self.relavent_agv_command,
                self.irrelavent_agv_command,
                self.relavent_task_command,
                self.irrelavent_task_command,
            ]
        ]

    def test_retrieve_all_relavent_commands_query(self):
        task = create_task()
        agv = create_agv(current_task_id=task.id)
        self._create_set_of_commands(agv, task)

        relavent_commands = CommandProcessingController._retrieve_all_relavent_commands_query(agv)

        # test relavent commands are still included
        self.assertEqual(len(relavent_commands), 6)
        expected_output_commands = [
            self.stop_command,
            self.stop_command,
            self.start_command,
            self.start_command,
            self.relavent_agv_command,
            self.relavent_task_command,
        ]
        for packet in zip(relavent_commands, expected_output_commands):
            command, expected_command = packet
            for key in ["agv_id", "task_id", "type"]:
                command_value = getattr(command, key) if hasattr(command, key) else None
                expected_command_value = expected_command.get(key, None)
                self.assertEqual(command_value, expected_command_value)

    def test_remove_invalid_relavent_commands(self):
        # this is done in order to make the originally relavent commands for cancel agv and task irrelavent
        task = create_task(status=TaskStatus.INCOMPLETE)
        agv = create_agv(current_task_id=task.id, status=AGVState.DONE)
        self._create_set_of_commands(agv, task)

        CommandProcessingController._remove_invalid_relavent_commands(agv)
        commands = CommandProcessingController._retrieve_all_relavent_commands_query(agv)

        # all start and stop commands should be removed
        self.assertEqual(commands, [])

    def test_retrieve_stop_agv_command(self):
        agv = create_agv()

        stop_agv_command = CommandProcessingController._retrieve_stop_agv_command(agv)
        self.assertEqual(stop_agv_command, None)

        stop_command = {
            "agv_id": agv.id,
            "type": CommandTypes.STOP_AGV,
        }
        early_stop_command = create_command(**stop_command)
        late_stop_command = create_command(**stop_command)

        stop_agv_command = CommandProcessingController._retrieve_stop_agv_command(agv)
        self.assertEqual(stop_agv_command.id, late_stop_command.id)

    def test_retrieve_start_agv_command(self):
        agv = create_agv()

        start_agv_command = CommandProcessingController._retrieve_start_agv_command(agv)
        self.assertEqual(start_agv_command, None)

        start_command = {
            "agv_id": agv.id,
            "type": CommandTypes.START_AGV,
        }
        early_start_command = create_command(**start_command)
        late_start_command = create_command(**start_command)

        start_agv_command = CommandProcessingController._retrieve_start_agv_command(agv)
        self.assertEqual(start_agv_command.id, late_start_command.id)

    def test_get_next_command(self):
        task = create_task(status=TaskStatus.IN_PROGRESS)
        agv = create_agv(current_task_id=task.id, status=AGVState.BUSY)

        stop_command = create_command(
            **{
                "agv_id": agv.id,
                "type": CommandTypes.STOP_AGV,
            }
        )
        start_command = create_command(
            **{
                "agv_id": agv.id,
                "type": CommandTypes.START_AGV,
            }
        )

        command = CommandProcessingController.get_next_command(agv)
        self.assertEqual(command.id, stop_command.id)

        Command.query.filter_by(id=stop_command.id).first().delete()
        agv_cancel_command = create_command(
            **{
                "agv_id": agv.id,
                "type": CommandTypes.CANCEL_AGV,
            }
        )

        command = CommandProcessingController.get_next_command(agv)
        self.assertEqual(command.id, start_command.id)

        Command.query.filter_by(id=start_command.id).first().delete()
        command = CommandProcessingController.get_next_command(agv)
        self.assertEqual(command.id, agv_cancel_command.id)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
