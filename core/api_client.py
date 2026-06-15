"""
API 客户端模块
提供 HTTP 请求封装和会话管理功能
"""

import requests
import logging

# 创建模块级别的 logger
logger = logging.getLogger(__name__)


def api_get(url, params=None, headers=None, timeout=10, response_type="json"):
    """
    封装 GET 请求
    
    Args:
        url: 请求URL
        params: URL参数
        headers: 请求头
        timeout: 超时时间
        response_type: 响应解析类型，可选值: "json" | "text" | "content"
    
    Returns:
        (status_code, response_data)
    """
    try:
        logger.info(f"GET {url} | params={params}")
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        logger.info(f"返回 {response.status_code} | 耗时 {response.elapsed.total_seconds():.2f}s")
        
        if response_type == "json":
            return response.status_code, response.json()
        elif response_type == "text":
            return response.status_code, response.text
        elif response_type == "content":
            return response.status_code, response.content
        else:
            logger.warning(f"未知的 response_type: {response_type}，默认使用 json")
            return response.status_code, response.json()
            
    except requests.exceptions.Timeout:
        logger.error(f"请求超时: {url}")
        return None, {"error": "timeout"}
    except requests.exceptions.ConnectionError:
        logger.error(f"连接失败: {url}")
        return None, {"error": "connection_error"}
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return None, {"error": str(e)}


def api_post(url, json_data=None, headers=None, timeout=10, response_type="json"):
    """
    封装 POST 请求
    
    Args:
        url: 请求URL
        json_data: JSON请求体
        headers: 请求头
        timeout: 超时时间
        response_type: 响应解析类型，可选值: "json" | "text" | "content"
    
    Returns:
        (status_code, response_data)
    """
    try:
        logger.info(f"POST {url} | data={json_data}")
        response = requests.post(url, json=json_data, headers=headers, timeout=timeout)
        logger.info(f"返回 {response.status_code} | 耗时 {response.elapsed.total_seconds():.2f}s")
        
        if response_type == "json":
            return response.status_code, response.json()
        elif response_type == "text":
            return response.status_code, response.text
        elif response_type == "content":
            return response.status_code, response.content
        else:
            logger.warning(f"未知的 response_type: {response_type}，默认使用 json")
            return response.status_code, response.json()
            
    except requests.exceptions.Timeout:
        logger.error(f"请求超时: {url}")
        return None, {"error": "timeout"}
    except requests.exceptions.ConnectionError:
        logger.error(f"连接失败: {url}")
        return None, {"error": "connection_error"}
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return None, {"error": str(e)}


def api_put(url, json_data=None, headers=None, timeout=10, response_type="json"):
    """
    封装 PUT 请求
    
    Args:
        url: 请求URL
        json_data: JSON请求体
        headers: 请求头
        timeout: 超时时间
        response_type: 响应解析类型，可选值: "json" | "text" | "content"
    
    Returns:
        (status_code, response_data)
    """
    try:
        logger.info(f"PUT {url} | data={json_data}")
        response = requests.put(url, json=json_data, headers=headers, timeout=timeout)
        logger.info(f"返回 {response.status_code} | 耗时 {response.elapsed.total_seconds():.2f}s")
        
        if response_type == "json":
            return response.status_code, response.json()
        elif response_type == "text":
            return response.status_code, response.text
        elif response_type == "content":
            return response.status_code, response.content
        else:
            logger.warning(f"未知的 response_type: {response_type}，默认使用 json")
            return response.status_code, response.json()
            
    except requests.exceptions.Timeout:
        logger.error(f"请求超时: {url}")
        return None, {"error": "timeout"}
    except requests.exceptions.ConnectionError:
        logger.error(f"连接失败: {url}")
        return None, {"error": "connection_error"}
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return None, {"error": str(e)}


def api_delete(url, params=None, headers=None, timeout=10, response_type="json"):
    """
    封装 DELETE 请求
    
    Args:
        url: 请求URL
        params: URL参数
        headers: 请求头
        timeout: 超时时间
        response_type: 响应解析类型，可选值: "json" | "text" | "content"
    
    Returns:
        (status_code, response_data)
    """
    try:
        logger.info(f"DELETE {url} | params={params}")
        response = requests.delete(url, params=params, headers=headers, timeout=timeout)
        logger.info(f"返回 {response.status_code} | 耗时 {response.elapsed.total_seconds():.2f}s")
        
        if response_type == "json":
            return response.status_code, response.json()
        elif response_type == "text":
            return response.status_code, response.text
        elif response_type == "content":
            return response.status_code, response.content
        else:
            logger.warning(f"未知的 response_type: {response_type}，默认使用 json")
            return response.status_code, response.json()
            
    except requests.exceptions.Timeout:
        logger.error(f"请求超时: {url}")
        return None, {"error": "timeout"}
    except requests.exceptions.ConnectionError:
        logger.error(f"连接失败: {url}")
        return None, {"error": "connection_error"}
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return None, {"error": str(e)}


def api_get_with_retry(url, params=None, headers=None, timeout=10, max_retries=3, backoff=1, retry_on_status=None, min_wait=0.5):
    """
    带重试机制的 GET 请求
    
    Args:
        url: 请求URL
        params: URL参数
        headers: 请求头
        timeout: 超时时间
        max_retries: 最大重试次数
        backoff: 退避系数
        retry_on_status: 需要重试的状态码列表，默认为 [500, 502, 503, 504]
        min_wait: 最小等待时间（秒）
    
    Returns:
        (status_code, response_data)
    """
    import time
    
    if retry_on_status is None:
        retry_on_status = [500, 502, 503, 504]
    
    last_response = None
    last_error = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"GET {url} | 第 {attempt + 1}/{max_retries} 次尝试")
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            logger.info(f"返回 {response.status_code} | 耗时 {response.elapsed.total_seconds():.2f}s")
            
            # 如果成功（状态码不在重试列表中），直接返回
            if response.status_code not in retry_on_status:
                if response.headers.get('content-type', '').lower().startswith('application/json'):
                    return response.status_code, response.json()
                else:
                    return response.status_code, response.text
                    
            last_response = response
            logger.warning(f"状态码 {response.status_code} 在重试列表中，准备重试")
            
        except requests.exceptions.RequestException as e:
            last_error = e
            logger.error(f"请求失败: {e}")
        
        # 计算等待时间
        wait_time = max(backoff * (attempt + 1), min_wait)
        logger.info(f"等待 {wait_time:.2f} 秒后重试")
        time.sleep(wait_time)
    
    # 达到最大重试次数，返回最后一次结果
    logger.error(f"已达到最大重试次数 {max_retries}")
    if last_response:
        try:
            return last_response.status_code, last_response.json()
        except:
            return last_response.status_code, last_response.text
    else:
        return None, {"error": str(last_error) if last_error else "unknown error"}


class ApiSession:
    """
    API 会话管理器
    提供带状态的 HTTP 请求能力，支持持久化 headers
    """
    
    def __init__(self, base_url):
        """
        初始化会话
        
        Args:
            base_url: API 基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        self._original_headers = self.session.headers.copy()
    
    def _request(self, method, path, params=None, json_data=None, headers=None, timeout=10, response_type="json", **kwargs):
        """
        内部通用请求方法，统一处理日志、异常和响应解析
        
        Args:
            method: HTTP方法，如 "GET", "POST", "PUT", "DELETE"
            path: API路径，如 "/api/user/info"
            params: URL参数（用于GET/DELETE）
            json_data: JSON请求体（用于POST/PUT）
            headers: 请求头（临时覆盖，不影响默认headers）
            timeout: 超时时间
            response_type: 响应解析类型，可选值: "json" | "text" | "content"
            **kwargs: 其他requests参数
        
        Returns:
            (status_code, response_data)
        """
        url = self.base_url + path
        
        if method in ("GET", "DELETE"):
            log_info = f"params={params}"
        else:
            log_info = f"data={json_data}"
            
        try:
            self.logger.info(f"{method} {url} | {log_info}")
            
            method_func = getattr(self.session, method.lower())
            
            if method in ("GET", "DELETE"):
                response = method_func(url, params=params, headers=headers, timeout=timeout, **kwargs)
            else:
                response = method_func(url, json=json_data, headers=headers, timeout=timeout, **kwargs)
            
            self.logger.info(f"返回 {response.status_code} | 耗时 {response.elapsed.total_seconds():.2f}s")
            
            if response_type == "json":
                return response.status_code, response.json()
            elif response_type == "text":
                return response.status_code, response.text
            elif response_type == "content":
                return response.status_code, response.content
            else:
                self.logger.warning(f"未知的 response_type: {response_type}，默认使用 json")
                return response.status_code, response.json()
                
        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时: {url}")
            return None, {"error": "timeout"}
        except requests.exceptions.ConnectionError:
            self.logger.error(f"连接失败: {url}")
            return None, {"error": "connection_error"}
        except Exception as e:
            self.logger.error(f"未知错误: {e}")
            return None, {"error": str(e)}

    def get(self, path, params=None, headers=None, timeout=10, response_type="json", **kwargs):
        """
        发送 GET 请求
        
        Args:
            path: API路径，如 "/api/user/info"
            params: URL参数
            headers: 请求头（临时覆盖，不影响默认headers）
            timeout: 超时时间
            response_type: 响应解析类型，可选值: "json" | "text" | "content"
            **kwargs: 其他requests参数
        
        Returns:
            (status_code, response_data)
        """
        return self._request("GET", path, params=params, headers=headers, timeout=timeout, response_type=response_type, **kwargs)
    
    def post(self, path, json_data=None, headers=None, timeout=10, response_type="json", **kwargs):
        """
        发送 POST 请求
        
        Args:
            path: API路径，如 "/api/login"
            json_data: JSON请求体
            headers: 请求头（临时覆盖，不影响默认headers）
            timeout: 超时时间
            response_type: 响应解析类型，可选值: "json" | "text" | "content"
            **kwargs: 其他requests参数
        
        Returns:
            (status_code, response_data)
        """
        return self._request("POST", path, json_data=json_data, headers=headers, timeout=timeout, response_type=response_type, **kwargs)

    def post_raw(self, path, data=None, headers=None, timeout=10, response_type="json", **kwargs):
        """
        发送 POST 请求（发送原始请求体，不自动转为JSON）
        
        Args:
            path: API路径，如 "/api/login"
            data: 原始请求体（字符串或字节），不自动转为JSON
            headers: 请求头（临时覆盖，不影响默认headers）
            timeout: 超时时间
            response_type: 响应解析类型，可选值: "json" | "text" | "content"
            **kwargs: 其他requests参数
        
        Returns:
            (status_code, response_data)
        """
        url = self.base_url + path
        try:
            self.logger.info(f"POST_RAW {url} | data_length={len(data) if data else 0} bytes")
            response = self.session.post(url, data=data, headers=headers, timeout=timeout, **kwargs)
            self.logger.info(f"返回 {response.status_code} | 耗时 {response.elapsed.total_seconds():.2f}s")
            
            if response_type == "json":
                try:
                    return response.status_code, response.json()
                except ValueError:
                    self.logger.warning(f"响应不是JSON格式，返回文本")
                    return response.status_code, response.text
            elif response_type == "text":
                return response.status_code, response.text
            elif response_type == "content":
                return response.status_code, response.content
            else:
                self.logger.warning(f"未知的 response_type: {response_type}，默认使用 json")
                return response.status_code, response.json()
                
        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时: {url}")
            return None, {"error": "timeout"}
        except requests.exceptions.ConnectionError:
            self.logger.error(f"连接失败: {url}")
            return None, {"error": "connection_error"}
        except Exception as e:
            self.logger.error(f"未知错误: {e}")
            return None, {"error": str(e)}

    def put(self, path, json_data=None, headers=None, timeout=10, response_type="json", **kwargs):
        """
        发送 PUT 请求
        
        Args:
            path: API路径，如 "/api/user/update"
            json_data: JSON请求体
            headers: 请求头（临时覆盖，不影响默认headers）
            timeout: 超时时间
            response_type: 响应解析类型，可选值: "json" | "text" | "content"
            **kwargs: 其他requests参数
        
        Returns:
            (status_code, response_data)
        """
        return self._request("PUT", path, json_data=json_data, headers=headers, timeout=timeout, response_type=response_type, **kwargs)

    def delete(self, path, params=None, headers=None, timeout=10, response_type="json", **kwargs):
        """
        发送 DELETE 请求
        
        Args:
            path: API路径，如 "/api/user/delete"
            params: URL参数
            headers: 请求头（临时覆盖，不影响默认headers）
            timeout: 超时时间
            response_type: 响应解析类型，可选值: "json" | "text" | "content"
            **kwargs: 其他requests参数
        
        Returns:
            (status_code, response_data)
        """
        return self._request("DELETE", path, params=params, headers=headers, timeout=timeout, response_type=response_type, **kwargs)

    def set_default_headers(self, headers):
        """
        设置默认请求头（持久化修改，影响后续所有请求）
        
        Args:
            headers: 字典类型的请求头
        """
        self.session.headers.update(headers)
        self.logger.info(f"已设置默认请求头: {headers}")
    
    def reset_headers(self):
        """
        重置请求头为初始状态
        """
        self.session.headers.clear()
        self.session.headers.update(self._original_headers)
        self.logger.info("已重置请求头为初始状态")
    
    def close(self):
        """
        关闭会话
        """
        self.session.close()
        self.logger.info("会话已关闭")


def configure_logging():
    """配置日志（可由主程序调用）"""
    import os
    
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    log_filename = os.path.join(os.path.dirname(__file__), 'api_client.log')
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(file_handler)

# 注意：configure_logging() 不再自动调用，由外部按需调用
