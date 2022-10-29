from logging import getLogger
from subprocess import run


class NodeExecutor:
    def __init__(self, cwd: str) -> None:
        self.__cwd = cwd
        self.__logger = getLogger(__name__)

    def execute(self, file_path: str) -> bytes:
        command = ["node", file_path]
        process = run(command, cwd=self.__cwd, capture_output=True)
        if process.returncode:
            self.__logger.error(
                f"Executing {command} failed. Stderr:\n{process.stderr.decode('utf8')}"
            )
        process.check_returncode()
        return process.stdout
