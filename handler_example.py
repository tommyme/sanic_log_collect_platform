import logging
import requests
import json
from expyutil.logging import setup_logger, default_color_fmter
import time


class HttpLogHandler(logging.Handler):
    def __init__(self, url, headers=None, timeout=5, data={}):
        """
        初始化HttpLogHandler

        参数:
        url (str): 用于发送日志的URL
        headers (dict, optional): 请求头,默认为None
        timeout (int, optional): 请求超时时间,默认为5秒
        """
        super().__init__()
        self.url = url
        self.headers = headers if headers else {"Content-Type": "application/json"}
        self.timeout = timeout
        self.data = data

    def emit(self, record):
        """
        将日志记录发送到后端

        参数:
        record (logging.LogRecord): 日志记录对象
        """
        try:
            log_data = {
                "logger": record.name,
                "level": record.levelname.lower(),
                "content": self.format(record),
            }
            log_data.update(self.data)
            st = time.time()
            response = requests.post(
                self.url,
                data=json.dumps(log_data),
                headers=self.headers,
                timeout=self.timeout,
            )
            ed = time.time()
            print(ed - st)
            response.raise_for_status()
        except (requests.exceptions.RequestException, ValueError):
            self.handleError(record)


logger = setup_logger("Executor")
data = {
    "chip": "1712",
    "version": "b300",
    "exectime": "2024-06-05 23:06:46",
    "case": "tc_bsbc_mainflow_02",
    "iter": 0,
}
handler = HttpLogHandler(
    "http://127.0.0.1:8000/addLog", data=data
)
handler.setFormatter(default_color_fmter)
logger.addHandler(handler)


for i in range(5):
    logger.info("hello world {}".format(i))
    logger.warning("hello world {}".format(i))
