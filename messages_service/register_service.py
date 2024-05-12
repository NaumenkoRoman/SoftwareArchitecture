import os
import consul

def register_service():
    consul_host = os.getenv("CONSUL_HOST", "localhost")
    service_name = os.getenv("SERVICE_NAME")
    service_port = int(os.getenv("SERVICE_PORT"))
    service_id = f"{service_name}-{service_port}"

    consul_client = consul.Consul(host=consul_host)
    consul_client.agent.service.register(
        name=service_name,
        service_id=service_id,
        address="localhost",
        port=service_port,
        tags=["microservice"]
    )
    print(f"Registered {service_name} with Consul")

if __name__ == "__main__":
    register_service()
