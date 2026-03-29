# CodeNexus Backend Microservices

This repository contains the **backend platform** that powers the CodeNexus VS Code extension.

> Important: the VS Code extension itself is in a separate repository. This codebase focuses only on backend services that the extension calls for analysis, detection, refactoring orchestration, auth/project workflows, and persistence.

## What this repo does

CodeNexus backend is a multi-service system that provides:

- Python AST parsing and static-analysis primitives.
- Code smell detection endpoints and task routing.
- Automated refactoring endpoints for supported smell classes.
- LLM-assisted architecture-smell detection/refactoring tasks.
- API gateway routing and data persistence models.
- Web/auth-related backend endpoints used by extension-integrated project workflows.

In short, this repo is the service layer behind the extension’s editor UI, diagnostics, quick-fix/refactor actions, dependency insights, and history/state features.

## Service architecture (high level)

The repository is organized into multiple services:

- **`api-gateway/` (FastAPI)**
  - Entry point/orchestrator used by clients.
  - Exposes endpoints for detection, refactor routing, websocket forwarding, and Mongo-related resources.

- **`ast-service/` (FastAPI)**
  - Parses Python code into AST-derived metadata.
  - Provides analyzers and visitors used for smell detection signals (imports, classes, functions, globals, unreachable blocks, etc.).

- **`refactoring-service/` (FastAPI)**
  - Applies deterministic source transformations for supported refactor types.
  - Hosts mapping/forwarding endpoints and transformer logic (e.g., dead code, magic number, naming, unused variable, unreachable).

- **`llm-service/` (Python service + jobs/prompts)**
  - Handles LLM-assisted detection/refactoring flows for higher-level architectural smells.
  - Includes task prompts, helper pipelines, and test fixtures for smells such as long function, god object, feature envy, inappropriate intimacy, middle man, and switch abuse.

- **`web-service/` (Node/Express-style service)**
  - Provides web/auth/project/ruleset/graph controllers used by account-aware or project-linked flows.

## How this backend integrates with the CodeNexus extension

The extension relies on this backend for server-side capabilities. Typical interaction flow:

1. A Python workspace is scanned in VS Code.
2. File payloads are sent to backend APIs for AST/detection processing.
3. Detection results are returned to extension diagnostics.
4. When the user triggers a refactor, extension requests backend refactor endpoints.
5. Refactor outputs and metadata are persisted/forwarded for history and rollback workflows.
6. Optional authenticated/project endpoints support account-scoped experiences.

### Integration responsibilities split

- **Extension repo**: editor UX, diagnostics rendering, tree views, commands, webviews, and local state presentation.
- **This repo**: analysis engines, refactor engines, orchestration APIs, data models, and service-to-service plumbing.

## Repository structure

```text
codenexus_microservices/
├── api-gateway/          # Main API surface + orchestration + persistence-facing endpoints
├── ast-service/          # AST parsing + static analysis utilities
├── refactoring-service/  # Refactoring transforms + endpoint mappings
├── llm-service/          # LLM-assisted smell detection/refactoring tasks
├── web-service/          # Auth/project/ruleset/graph backend controllers
└── README.md
```

## Local run guide

Each service is started independently from its own directory.

### 1) API Gateway

```bash
cd api-gateway
python -m uvicorn app.main:app --port 8000 --reload
```

### 2) AST Service

```bash
cd ast-service
python -m uvicorn app.main:app --port 8001 --reload
```

### 3) Refactoring Service

```bash
cd refactoring-service
python -m uvicorn app.main:app --port 8002 --reload
```

### 4) LLM Service

```bash
cd llm-service
python main.py
```

### 5) Web Service

```bash
cd web-service
npm install
npm run dev
```

## Suggested startup order

1. Data/messaging dependencies (if used in your environment, e.g., localstack/SQS, database).
2. `ast-service`
3. `refactoring-service`
4. `llm-service`
5. `api-gateway`
6. `web-service` (if auth/project web endpoints are required)

## Dependency and environment notes

- Python services use per-service `requirements.txt` files.
- Node dependencies are under `web-service/package.json`.
- Some flows require external infrastructure (e.g., queueing, persistence, auth providers) depending on your configured environment.
- Service URLs/port mappings should align with extension-side configuration in the extension repository.

## Testing

The repo includes service-level tests under service-specific `testing/` or `test/` directories (for example in `ast-service/`, `refactoring-service/`, and `llm-service/`). Run tests from each service directory using that service’s preferred test command/tooling.

## Scope and non-goals

- This repository does **not** include VS Code extension UI/activation code.
- This repository does **not** document extension packaging or editor host lifecycle details beyond backend integration points.
- The purpose of this README is to help backend contributors and extension integrators understand service responsibilities and integration boundaries.
