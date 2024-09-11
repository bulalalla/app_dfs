import subprocess
import os
import signal


class BackgroundTask:
    
    def __init__(self, tasks: dict) -> None:
        if not isinstance(tasks, dict):
            raise "Error"
        self.tasks = dict()
        for k, v in tasks.items():
            self.add(task_id=k, task_cmd=v)
        
    def add(self, task_id: str, task_cmd: list):
        proccess = subprocess.Popen(
            task_cmd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        self.tasks.update({task_id: [task_cmd, proccess]})

    def status_of(self, task_id):
        # True 仍然在运行 False 已经执行完毕
        return True if isinstance(self.tasks[task_id][1].poll(), None) else False
    
    def delete(self, task_id):
        if task_id in self.tasks.keys():
            del self.tasks[task_id]

    def stop(self, task_id):
        # 可以选择多种方式来杀死子进程，详见Popen对象的方法
        if task_id in self.tasks.keys() and not self.tasks[task_id][1].poll():
            self.tasks[task_id][1].send_signal(signal.CTRL_BREAK_EVENT)

    def returncode(self, task_id):
        if task_id in self.tasks.keys():
            self.tasks[task_id][1].poll()
            return self.tasks[task_id][1].returncode
        
    def stop_all(self):
        for task_id, _ in self.tasks.items():
            self.stop(task_id)