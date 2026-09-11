import threading


class RobotWorker:
    def __init__(self, robot):
        self.robot = robot

        self.thread = None

        self.stop_event = threading.Event()

        self.is_running = False

    def start_task(
        self,
        target,
        *args
    ):
        if self.is_running:
            print("Robot is already running.")
            return False

        self.stop_event.clear()
        self.is_running = True

        self.thread = threading.Thread(
            target=self._run_task,
            args=(target, *args),
            daemon=True
        )

        self.thread.start()

        return True

    def _run_task(
        self,
        target,
        *args
    ):

        try:
            target(
                self.robot,
                self.stop_event,
                *args
            )
        
        except Exception as error:
            print()
            print(f"Robot task error: {error}")

        finally:
            self.is_running = False

    def emergency_stop(self):
        print()
        print("Emergency stop requested.")

        self.stop_event.set()

        self.robot.emergency_stop()