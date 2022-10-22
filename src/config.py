from typing import Dict

from common.fastapi.core.parameters import get_param_manager
from common.fastapi.core.parameters.managers import Definition, Environ
from common.fastapi.core.parameters.parameter_manager import ParameterManager
from kubernetes import config, client
from kubernetes.client import AppsV1Api, CoreV1Api, Configuration, ApiClient


class Config(ParameterManager):
    is_simulation: bool = Definition(True)
    k8s_api_key: Dict = Environ(dict())
    k8s_api_key_prefix: Dict = Environ(dict())
    k8s_host: str = Environ("http://localhost:443")
    k8s_password: str = Environ(None)
    k8s_username: str = Environ(None)

    @staticmethod
    def get_k8s_config():
        params = get_param_manager()
        configuration = Configuration(
            host=params.variables.k8s_host,
            api_key=params.variables.k8s_api_key,
            password=params.variables.k8s_password,
            username=params.variables.k8s_username,
            api_key_prefix=params.variables.k8s_api_key_prefix,
            discard_unknown_keys=False
        )

        return configuration

    @staticmethod
    def get_k8_client() -> AppsV1Api:
        configuration = Config.get_k8s_config()
        api_client = ApiClient(configuration=configuration)
        k8s_client = client.AppsV1Api(api_client)
        return k8s_client

    @staticmethod
    def get_k8s_core_api() -> CoreV1Api:
        configuration = Config.get_k8s_config()
        api_client = ApiClient(configuration=configuration)
        k8s_client = client.CoreV1Api(api_client)
        return k8s_client
