# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A waste management platform with smart bin monitoring, waste collector routing, pricing, and notifications. The system is event-driven and microservices-based, deployed on Kubernetes.

See the high-level design: [docs/architecture/high-level-design.png](docs/architecture/high-level-design.png)

## Architecture

The system follows an event-driven microservices pattern:


- **Load Balancer** — distributes traffic across multiple API instances
- **Waste Collector API** — core REST API (Django REST Framework), connects to MongoDB and publishes to the Event Bus
- **Event Bus** (Kafka) — decouples the API from downstream services
- **Pricing Service** — subscribes to events to calculate and update pricing
- **Notification Service** — subscribes to events to send alerts/notifications
- **Smart Bin Manager Service** — manages smart bin state; communicates with physical bins via Smart Bin API
- **Payment Service** — handles payment processing
- **Database** — MongoDB (shared by the Waste Collector API)

## Expected Folder Structure

```
west-collector-svc/          # Django REST framework
  |-- k8s-config/            # Kubernetes manifests (deployment, service namespace)
  |-- .gitignore             # to exclude some secure files
  |-- core-app/              # The core app and its functionility

pricing-svc/                 # Django REST framework
  |-- k8s-config/            # Kubernetes manifests (deployment, service namespace)
  |-- .gitignore             # to exclude some secure files
  |-- core-app/              # The core app and its functionility
  
notification-svc/            # Django REST framework
  |-- k8s-config/            # Kubernetes manifests (deployment, service namespace)
  |-- .gitignore             # to exclude some secure files
  |-- core-app/              # The core app and its functionility
  
smart-bim-mgmt-svc/          # Django REST framework
  |-- k8s-config/            # Kubernetes manifests (deployment, service namespace)
  |-- .gitignore             # to exclude some secure files
  |-- core-app/              # The core app and its functionility
  
  setup.cfg                  # main config file for whole setup through k8s
```


## Commands



### Kubernetes
```bash
kubectl apply -f frontend/k8s-config/namespace.yaml
kubectl apply -f frontend/k8s-config/deployment.yaml
kubectl apply -f frontend/k8s-config/service.yaml
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| service | Django REST |
| Database | SQLite |
| Container | Docker (nginx:alpine to serve built frontend) |
| Orchestration | Kubernetes |
| Maps | Google Maps |


## Design pattern and System design

Use all available design pattern and system design for each services and a good entity
structure for better result and faster responce.
Like- Decorator design pattern, Observer, etc.