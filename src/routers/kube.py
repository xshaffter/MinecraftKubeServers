import os
import random
from datetime import datetime
from time import sleep

import yaml
from common.fastapi.db import CRUDDal, get_dal_dependency, get_dal
from common.fastapi.routing import post, BaseRouter, delete
from common.fastapi.schemas import HTTP_201_CREATED, HTTPResponseModel, HTTP_200_REMOVED
from fastapi import Path, Depends, Body
from kubernetes.client import V1Service, V1ServiceList

from src import Config
from src.db.models.enums.modality import Modality
from src.db.models.service import Service
from src.db.models.world import World
from src.schemas import WorldData


class KubeRouter(BaseRouter):

    @post('/service/create/{service_type}', response_model=HTTPResponseModel)
    def start_service(self, service_type: Modality,
                      service_dal: CRUDDal[Service] = Depends(get_dal_dependency(CRUDDal, Service))):

        service_dal._auto_commit = False
        used_ports = [service.used_port for service in service_dal.list(service_type=service_type.name, is_active=True)]
        service_count = service_dal.get_object_query(service_type=service_type.name, is_active=True).count() + 1
        service_middlescore = service_type.name.replace("_", "-")
        service_name = f"{service_middlescore}-{service_count}"

        world_dal = get_dal(CRUDDal, World)
        world = world_dal.get_object(world_type=service_type.name, world_identifier=service_count)

        if not world:
            return HTTPResponseModel(
                status_code=404,
                detail=dict(
                    detail='No lobbies left for this modality'
                )
            )

        with open('base_kube_yamls/minecraft-server.yaml') as mine_yaml:
            file_content = "".join(mine_yaml.readlines()) \
                .replace("{{service-name}}", service_name) \
                .replace("{{world-volume}}", world.world_path)

        with open('base_kube_yamls/load-balancer.yaml') as mine_yaml:
            rnd_port = random.randint(40000, 50000)
            while rnd_port in used_ports:
                rnd_port = random.randint(40000, 50000)
            service_file_content = "".join(mine_yaml.readlines()).replace("{{service-name}}", service_name)\
                .replace("{{service-port}}", f"{rnd_port}")

        new_yaml = f'yamls/{service_name}.yaml'
        new_yaml_fw = f'yamls/{service_name}-fw.yaml'

        host = None
        with open(new_yaml, "w+") as deployment_yaml:
            deployment_yaml.write(file_content)

        with open(new_yaml_fw, "w+") as service_yaml:
            service_yaml.write(service_file_content)

        with open(new_yaml_fw) as service_yaml:
            service_instance = yaml.safe_load(service_yaml)
            client = Config.get_k8s_core_api()
            response: V1Service = client.create_namespaced_service(body=service_instance, namespace="default")
            port = response.spec.ports[0].port

        with open(new_yaml) as deployment_yaml:
            instance = yaml.safe_load(deployment_yaml)
            client_app = Config.get_k8_client()
            client_app.create_namespaced_deployment(body=instance, namespace="default")

        client = Config.get_k8s_core_api()
        search = True
        while search:
            services: V1ServiceList = client.list_namespaced_service(namespace="default")
            for serv in services.items:  # type: V1Service
                if serv.metadata.name == f"{service_name}-server":
                    try:
                        host = serv.status.load_balancer.ingress[0].ip
                        search = False
                    except IndexError:
                        host = None
                    except TypeError:
                        host = None
                    break
            sleep(10)

        service_dal.create(dict(
            service_path=new_yaml,
            service_type=service_type.name,
            service_name=service_name,
            started_at=datetime.now(),
            used_port=f"{host}:{port}"
        ))
        service_dal.commit()

        return HTTPResponseModel(status_code=200, detail=dict(
            service_name=service_name,
            url_path=f"{host}:{port}"
        ))

    @delete('/service/stop/{service_name}', response_model=HTTPResponseModel)
    def stop_service(self, service_name: str,
                     service_dal: CRUDDal[Service] = Depends(get_dal_dependency(CRUDDal, Service))):
        service: Service = service_dal.get_object(service_name=service_name, is_active=True)
        client = Config.get_k8s_core_api()
        client_app = Config.get_k8_client()
        try:
            os.remove(f"/app/yamls/{service_name}-fw.yaml")
            os.remove(f"/app/yamls/{service_name}.yaml")
            os.remove(service.service_path)
        except:
            pass

        service_dal.update(dict(
            is_active=False,
            stopped_at=datetime.now()
        ), service_name=service_name, is_active=True)

        try:
            client.delete_namespaced_service(f"{service_name}-server", namespace="default")
            client_app.delete_namespaced_deployment(f"{service_name}-deployment", namespace="default")
        except:
            return HTTPResponseModel(status_code=200, detail=dict(
                detail="removed service"
            ))
        return HTTP_200_REMOVED

    @post('/world/create', response_model=HTTPResponseModel)
    def create_world(self, world_data: WorldData,
                     world_dal: CRUDDal[World] = Depends(get_dal_dependency(CRUDDal, World))):
        data_dict: dict = world_data.dict()
        data_dict["world_type"] = world_data.world_type.name
        world_dal.create(data_dict)

        return HTTP_201_CREATED
