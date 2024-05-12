import os
import consul

def register_service():
    consul_host = os.getenv("CONSUL_HOST", "localhost")
    service_name = os.getenv("SERVICE_NAME")
    service_port = int(os.getenv("SERVICE_PORT"))
    service_id = f"{service_name}-{service_port}"

    service_address = service_name.replace("-", "_")  # Docker service names are hyphen-separated

    consul_client = consul.Consul(host=consul_host)
    consul_client.agent.service.register(
        name=service_name,
        service_id=service_id,
        address=service_address,
        port=service_port,
        tags=["microservice"]
    )
    print(f"Registered {service_name} with Consul at {service_address}:{service_port}")

if __name__ == "__main__":
    register_service()
