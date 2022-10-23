import os
from typing import Dict

from common.fastapi.core.parameters import get_param_manager
from common.fastapi.core.parameters.managers import Definition, Environ
from common.fastapi.core.parameters.parameter_manager import ParameterManager
from kubernetes import config, client
from kubernetes.client import AppsV1Api, CoreV1Api, Configuration, ApiClient


class Config(ParameterManager):
    is_simulation: bool = Definition(True)
    k8s_config_file: str = Definition("/static/k8s-config.yaml")

    @staticmethod
    def get_k8s_config():
        config.load_kube_config(
            config_file=get_param_manager().variables.k8s_config_file,
        )

        params = get_param_manager()

    @staticmethod
    def get_k8_client() -> AppsV1Api:
        Config.get_k8s_config()
        api_client = ApiClient()
        k8s_client = client.AppsV1Api(api_client)
        return k8s_client

    @staticmethod
    def get_k8s_core_api() -> CoreV1Api:
        Config.get_k8s_config()
        api_client = ApiClient()
        k8s_client = client.CoreV1Api(api_client)
        return k8s_client
