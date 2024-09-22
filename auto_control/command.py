import subprocess
import signal
import time


class Task:
    """
        需要使用cmd执行的命令行被定义为Task
    """
    # created_task = set()

    def __init__(self, task_id: str, task_cmd: list[str], slow: bool) -> None:
        
        # if task_id in self.created_task:
        #     raise f"{task_id}已经被创建"
        
        self.id = task_id
        self.cmd = task_cmd
        self.slow = slow
        self.status: str = ["CREATE", "RUNNING", "RUN_OVER", "RECV", "ERROR"]
        self.status = "CREATE"
        self.process: subprocess.Popen = None
        self.exe_result_str: str = None
        self.exe_result: dict = None
        self.res_dealwith_tbl = {
            "": self.dealwtih_result_str
        }

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Task) and self.id == value.id

    def __hash__(self) -> int:
        return self.id.__hash__()

    def run(self):
        """
            运行这个task
        """
        if self.status == "CREATE":
            try:
                process = subprocess.Popen(
                        self.cmd,
                        stdout=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        shell=True
                    )
                self.status = "RUNNING"
                self.process = process
                time.sleep(1)   # 起码给出1秒的时间执行
            except:
                self.status = "ERROR"

    def stop(self):
        """
            停止这个task，状态应该设置为 RUN_OVER
        """
        if self.status == "RUNNING":
            if self.process:
                if self.process.poll():
                    self.status = "RUN_OVER"
                else:
                    self.process.terminate()
                    self.status = "RUN_OVER"
        elif self.status == "CREATE":
            print(f"you should run {self.id} first")

    def recv(self):
        """
            接收并处理task的标准输出
        """
        if self.process.poll() and self.status in ["CREATE", "RUNNING"]:
            self.status = "RUN_OVER"
        if self.status == "RUN_OVER":        
            self.exe_result_str = self.process.stdout.read()
            # TODO 对运行结果的标准输出做处理
            self.exe_result = {}
            self.status = "RECV"
            return self.exe_result

    def is_running(self):
        if self.status == "RUNNING" and not self.process.poll():
            return True
        else:
            if self.status == "RUNNING":
                self.status = "RUN_OVER"
        return False

    # 这里可以根据不同的任务处理
    def dealwtih_result_str(self):
        pass


class TaskManager:
    
    def __init__(self, tasks: list[Task] | None) -> None:
        self.tasks_list = tasks

    def add_and_run(self, task: Task):
        self.tasks_list.append(task)
        self.tasks_list[-1].run()

    def run_all(self, tasks=None):
        if not tasks:
            for task in self.tasks_list:
                task.run()
        else:
            for task in tasks:
                task.run()

    def stop_all(self, tasks=None):
        if not tasks:
            for task in self.tasks_list:
                task.stop()
        else:
            for task in tasks:
                task.stop()


    def recv_all(self, tasks=None):
        if not tasks:
            for task in self.tasks_list:
                task.recv()
        else:
            for task in tasks:
                task.recv()


    def find_task(self, task_id):
        index = -1
        for i in range(len(self.tasks_list)):
            if self.tasks_list[i].id == task_id:
                index = i
        return None if index == -1 else self.tasks_list[index]
    
    def find_slow_task(self, slow=True):
        res = []
        for task in self.tasks_list:
            if task.slow == slow:
                res.append(task)
        return res

    def is_runover(self, tasks: list[str] | list[Task]):
        """
            检测这些任务是否都已经执行完毕
        """
        res = []
        for task in tasks:
            if isinstance(task, Task):
                task_id = task.id
            else:
                task_id = task
            task = self.find_task(task_id=task_id)
            if not task.is_running():
                res.append(True)
            else:
                res.append(False)
        return res


if __name__ == "__main__":
    l = [Task(task_id='abc', task_cmd=['abc'], slow=True)]
    def fu(a):
        a.append(Task(task_id='abc', task_cmd=['abc'], slow=True))
        return a
    l2 = fu(l)
    t = l2[0]
    t.cmd = 'hhhhhhhhhhh'
    for task in l:
        print(task.cmd)

    for task in l2:
        print(task.cmd)