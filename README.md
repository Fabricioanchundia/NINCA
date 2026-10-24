# Ninca — Estado del proyecto

Escáner de seguridad para servidores MCP (portafolio de Fabricio).
Repo: https://github.com/Fabricioanchundia/NINCA
Dashboard: https://fabricioanchundia.github.io/NINCA/
Demo interactiva: https://fabricioanchundia.github.io/NINCA/try.html

## Stack
- Python 3.12, uv, src-layout
- DuckDB (almacenamiento), httpx (HTTP)
- Ollama + qwen2.5:7b en GPU (RTX 5060) para el clasificador IA
- Docker, GitHub Action, GitHub Pages (dashboard Chart.js)
- Git: ramas feature, Conventional Commits, PRs squash, pre-commit, CI (ruff/mypy/pytest)

## Los 4 pilares (visión original)
- [x] **Data** — discovery + github + storage + pipeline. 33,477 servidores en DuckDB.
- [x] **IA** — ai.py (clasificador Ollama) + hybrid.py (reglas + IA). Guarda descripciones/metadata, NO el código (decisión ética).
- [~] **Ciberseguridad** — scanner.py (6 reglas), evaluación (precisión 100%, recall ~86% híbrido), rug pull, autodefensa, y guard.py (decisión conectar/bloquear). FALTA solo divulgación responsable.
- [x] **Cloud/DevOps** — action.yml, Dockerfile, CI, scan-demo.yml, dashboard público.

## Cómo protege a los agentes (3 niveles)
- [x] **Nivel 1 — Auditoría**: `ninca scan tools.json` o la web. Informa.
- [x] **Nivel 2 — Puerta CI**: la GitHub Action bloquea builds con herramientas envenenadas.
- [x] **Nivel 3 — Guardia en vivo**: `ninca guard tools.json` → ALLOW/BLOCK + código de salida (1 = bloqueado). Flag `--strict` bloquea también severidad alta. Solo lee descripciones (nunca ejecuta el servidor).

## Fases
- [x] Fases 0–10 completas (setup, data, scanner, IA, híbrido, Docker, Action, dashboard)
- [x] Demo web try.html — rediseño profesional serio (IBM Plex, sin emojis), bilingüe ES/EN, acepta JSON de servidor, puntaje de riesgo, copiar informe
- [x] `ninca guard` — Nivel 3, fusionado a main (commit 0cbb19f)
- [ ] **Fase 11 — Divulgación responsable** (política SECURITY.md + plantilla para avisar a autores)
- [ ] **Fase 12 — Informe "Estado de seguridad MCP 2026" + README pro + video demo + post LinkedIn**

## Pendientes menores / opcionales
- [ ] Mostrar `ninca guard` en la web (footer de try.html) y en el README.
- [ ] App web local con IA real (FastAPI + Ollama) — la IA ya funciona en el CLI; esto sería solo una interfaz web. Fuera del plan original.

## Métricas de evaluación
- Reglas solas: recall ~57% | Híbrido (reglas+IA): recall ~86% | Precisión: 100% en todos.

## Recordatorio de flujo (trampa recurrente)
Si pre-commit dice "Failed / files were modified" → `git add` + `git commit` OTRA VEZ.
El `push` va SOLO cuando aparece la línea `[rama XXXXXXX]`.
Comando a prueba de fantasma: `git add <archivos> && git commit -m "msg" || { git add <archivos> && git commit -m "msg"; }`
