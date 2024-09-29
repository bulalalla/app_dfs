import subprocess
import signal
import time
import re


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
        self.exe_result: dict = {}
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
                print(f"start task: {self.id}")
                time.sleep(1)   # 起码给出1秒的时间执行
            except:
                self.status = "ERROR"

    def stop(self):
        """
            停止这个task，状态应该设置为 RUN_OVER
        """
        if self.status == "RUNNING":
            if self.process:
                self.process.terminate()
                self.process.wait()
                self.status = "RUN_OVER"
                print(f"end   task: {self.id}")
        elif self.status == "CREATE":
            print(f"you should run {self.id} first")

    def recv(self):
        """
            接收并处理task的标准输出
        """
        if self.status == "RUNNING":
            self.stop()
        elif self.status == "CREATE":
            print(f"you should run {self.id} first.")
        
        if self.status == "RUN_OVER":        
            self.exe_result_str = self.process.communicate()[0].decode()
            # TODO 对运行结果的标准输出做处理
            self.status = "RECV"
            return self.exe_result_str
        

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

    def dealwith_adb(self):
        res_str = self.exe_result_str.lower()
        if "unsuccess" in res_str or "cannot" in res_str or "failed" in res_str:
            self.status = "ERROR"
            return -1
        return 0
    
    def dealwith_aapt(self):
        aapt_output = self.process.communicate()[0].decode()
        # 筛选出 package 和 activity 信息
        package_pattern = re.search(r"package: name='([^']+)'", aapt_output)
        activity_pattern = re.search(r"launchable-activity: name='([^']+)'", aapt_output)

        # 如果没有获取到名称，就不继续执行
        if package_pattern and activity_pattern:
            self.exe_result.update({
                "app_package_name": package_pattern.group(1),
                "app_activity_name": activity_pattern.group(1)
            })
        else:
            raise "init error, not find app_package_name or app_activity_name"
        return 0

    def dealwith_tcpdump(self):
        return 0

    def dealwith_mitmproxy(self):
        return 0



class TaskManager:
    
    def __init__(self, tasks: list[Task] | None) -> None:
        if tasks == None:
            self.tasks_list = list()
        else:
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
    import pandas as pd
    import mysql.connector

    # 连接到数据库
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='1234',
        database='app_doe'
    )

    # 查询获取不重复的 hosts
    query = """
    SELECT package_name, host
    FROM app_domain_https WHERE add_time > '2024-09-29 11:00:00'
    GROUP BY package_name, host;
    """
    cursor = conn.cursor()
    cursor.execute(query)

    # 获取所有结果
    results = cursor.fetchall()

    # 将结果转换为 DataFrame
    df = pd.DataFrame(results, columns=['package_name', 'host'])

    count = 0
    for row in df['host']:
        print(row)
        host = str(row)
        count += len(host.split(','))
    print(count)
        


    # 将数据透视为每个 package_name 一列
    df_pivot = df.pivot_table(index=df.groupby('package_name').cumcount(), columns='package_name', values='host', aggfunc='first')

    # 将结果保存到 Excel
    # df_pivot.to_excel('output.xlsx', index=False)

    # 关闭连接
    cursor.close()
    conn.close()

        
