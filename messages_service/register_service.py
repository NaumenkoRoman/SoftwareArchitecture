import os
import consul

def register_service():
    consul_host = os.getenv("CONSUL_HOST", "consul")
    service_container_name = os.getenv("SERVICE_CONTAINER_NAME")
    service_name = os.getenv("SERVICE_NAME")
    service_port = int(os.getenv("SERVICE_PORT"))
    service_id = f"{service_container_name}-{service_port}"


    consul_client = consul.Consul(host=consul_host)
    consul_client.agent.service.register(
        name=service_name,
        service_id=service_id,
        address=service_container_name,
        port=service_port,
        tags=["microservice"]
    )
    print(f"Registered {service_name} with Consul at http://{service_container_name}:{service_port}")

if __name__ == "__main__":
    register_service()
