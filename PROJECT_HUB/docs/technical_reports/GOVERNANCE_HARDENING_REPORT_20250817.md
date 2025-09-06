# Governance Hardening Report (Stand: 2025‑08‑17)

Ziel: Verbindliche Regeln, Prozesse und Kontrollen, die Betrieb, Sicherheit und Verfassungskonformität dauerhaft sicherstellen – ohne Entwicklungsfluss zu behindern.

## 1) Policy as Code (PaC)
- Maßnahme: Richtlinien als Versionierte Regeln
  - Zugriffsregeln, Schreib‑/Bulk‑Policies, Export‑/Provenienz‑Regeln, Ethik‑Gates
  - Umsetzung (Stufe 1): Lightweight‑Rules in App/Proxy, YAML/JSON im Repo
  - Perspektive: OPA/Gatekeeper (K8s) für Clusterweite Policies
- Akzeptanz: Jede risikobehaftete Route/Operation referenziert eine Rule‑ID; PRs ändern Policies nur mit Review.

## 2) Rollen & Scopes (RBAC)
- Rollen: reader, writer, admin (+ optional auditor)
- Scopes: facts:read, facts:write, facts:bulk, admin:limits, admin:export
- Durchsetzung:
  - `/api/*` Scopes: read/write/bulk (je nach Route)
  - `/api-admin/*` nur admin (+ optional auditor für read‑only Admin‑Infos)
- Akzeptanz: Unzureichende Scopes → 403; Audit protokolliert (who/what/when/why).

## 3) Change‑Control & Release‑Gates
- PR‑Checkliste (Pflicht):
  - [ ] Security‑Diff: betroffene Policies/Scopes genannt
  - [ ] SAST/DAST grün; SBOM aktualisiert
  - [ ] Rollback‑Plan + Impact‑Beurteilung
  - [ ] Secrets nicht im Diff (Scanner)
- Release‑Gate: Block bei kritischen Findings; Notfall‑Rollback dokumentiert.

## 4) Incident‑Response (IR)
- Runbook: Erkennung → Klassifizierung → Eindämmung → Forensik → Recovery → Post‑Mortem
- Rollen: Incident Commander, Comms, Forensik, Ops
- Akzeptanz: Innerhalb 15 Min. IR‑Call/Channel aktiv; erste Eindämmung < 60 Min.

## 5) Audit & Nachvollziehbarkeit
- Append‑only Audit‑Logs (Write‑Events, Policy‑Bypässe, Admin‑Aktionen)
- Pflichtfelder: actor, action, resource, scope, policy_id, ts, reason
- Tamper‑Evidenz: Write‑Ahead‑Hash‑Kette oder externer Append‑Store
- Akzeptanz: Vollständige Kette pro Write rekonstruierbar; Audit‑Export ohne PII.

## 6) Daten‑Governance
- Provenienz: Jede Fakt‑Write mit `source`, `method`, `confidence`
- Exporte: PII‑Redaction, Export‑Scopes (auditor/admin), Audit‑Trail
- Retention: Aufbewahrung/Aufräumen je Kategorie; Backups mit Katalog
- Akzeptanz: Write ohne Provenienz → 400; Exporte nur mit Scope; Retention‑Jobs belegt.

## 7) Secrets & Schlüsselverwaltung
- Speicher: Windows Credential Manager (dev), KeyVault (prod)
- Rotation: Kalender + Script + Dry‑Run; Zero‑Downtime Rotationspfad
- Masking: Keine Secrets in Logs/Traces/UI
- Akzeptanz: Erfolgreiche Rotation im Test; Scans finden keine Secrets im Repo/Logs.

## 8) 4‑Augen‑Prinzip & Freigaben
- Erforderlich für: Bulk‑Writes, Policy‑Änderungen, Export großer Datenmengen
- Umsetzung: 
  - Git‑PR mit mind. 1 Reviewer und „approval‑commit“
  - UI‑Workflows mit Co‑Sign‑Token (2nd factor)
- Akzeptanz: Ohne 2. Signatur wird Vorgang geblockt; Audit hat beide Akteure.

## 9) Operability & Safe‑Debugging
- Ein‑Origin Proxy + Pfad‑Trennung (`/api` ↔ `/api-admin`) → risikoarmes Umschalten
- Sauberer Neustart: `scripts/restart_all_ps7_orchestratedONLY.ps1`
- Sichtbare Logs (Caddy Foreground), Health/WS‑Probes via 8088
- Akzeptanz: Troubleshooting ohne Code‑/ENV‑Wechsel möglich; keine CORS‑Nebeneffekte.

## 10) Schulung & Dokumentation
- Pflichtlektüre: START_GUIDE_LOCAL_DEV_8088, START_SEQUENCE_PS7, MASTER_SECURITY_OPERABILITY_PLAN, SECURITY_MATURITY_PLAN_STAGE5
- Onboarding‑Session (2h): Policies, Scopes, IR‑Drill
- Akzeptanz: Neue Teammitglieder bestehen „Security‑Onboarding Quiz“.

## 11) Compliance‑Mapping (leichtgewichtig)
- Zuordnung Policies→Kontrollen (Transport, Auth, Audit, Backup)
- Evidence‑Ordner: Pipeline‑Reports, Audit‑Proben, Restore‑Protokolle
- Akzeptanz: Stichprobe zeigt vollständige Belege pro Kontrollpunkt.

## 12) Roadmap & OKRs (Q3–Q4)
- OKR‑Sicherheit: TLS/H3 + RBAC/JWT produktiv, 0 kritische SAST/DAST Findings, Rotation geübt
- OKR‑Operability: MTTR < 30 Min; Restore‑Test < 15 Min; 100% Einhaltung PR‑Checklisten

## 13) Offene Risiken & Mitigation
- Overhead OTel/eBPF → Sampling/P50‑Pfad
- Human Factor → Schulung, Just‑in‑Time‑Grants, Re‑Zertifizierung Rechte
- FFI‑Risiken → Stable ABI, Tests, Fallbacks auf Python‑Pfad

---

### Verweise
- Operability/Security Pläne: 
  - `PROJECT_HUB/MASTER_SECURITY_OPERABILITY_PLAN.md`
  - `PROJECT_HUB/SECURITY_MATURITY_PLAN_STAGE5.md`
  - `PROJECT_HUB/FUTURE_DEVELOPMENT_PLAN_2025H2.md`
- Start/Orchestrierung:
  - `PROJECT_HUB/START_GUIDE_LOCAL_DEV_8088.md`, `PROJECT_HUB/START_SEQUENCE_PS7.md`
  - `scripts/restart_all_ps7_orchestratedONLY.ps1`, `scripts/start_caddy.ps1`

Stand: 2025‑08‑17 – Verantwortlich: GPT‑5 (Handover an Claude Opus für Policy‑Implementierung & Reviews)

