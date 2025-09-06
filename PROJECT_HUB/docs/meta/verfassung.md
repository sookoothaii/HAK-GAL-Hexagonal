# HAK/GAL Verfassung v2.2 (operationalisierte Fassung)

Diese Fassung ist die präzise, umsetzbare Zusammenführung von JSON-Policy, SMTKernlogik und praktischen Betriebsregeln für den autonomen HexBackend (Port 5001) und MCPReadOnlyIntegration.

## Zielbild
- Externe Legalität hat Vorrang (kein Override möglich).
- StandardGate ist streng, OverrideGate streng kontrolliert.
- Nachvollziehbare Messmodelle, deterministische Prüfung, auditierbare Entscheidungen.

## Formale Kernlogik (Summary)
- Allowed(a) := ExternallyLegal(a)  (PassesDefaultEthic(a)  PassesOverride(a))
- PassesDefaultEthic(a) := Universalizable(a)  HarmHumanProb(a)  0.001  SustainIndex(a)  0.85
- PassesOverride(a) := OperatorOverride(a)  PeerReviewed(a)  OverrideDocProvided(a)  RiskExceptionJustified(a)
- Grenzen: 0  HarmHumanProb  1, 0  SustainIndex  1
- Externe Illegalität kann niemals überschrieben werden.

## Prinzipien (P1P7, komprimiert)
- P1 Komplementäre Intelligenz: passende Aufgabenzuteilung (symbolisch/neural/menschlich)
- P2 Gezielte Befragung: präzise, testbare Eingaben und Metriken
- P3 Externe Verifikation: unabhängiger Nachweis
- P4 Bewusstes Grenzüberschreiten: diagnostische Fehler provozieren, Ursachen verstehen
- P5 SystemMetareflexion: wiederkehrende Selbstanalyse
- P6 Empirische Validierung: quantitative, reproduzierbare Evidenz
- P7 Konjugierte Zustände: Tradeoffs zwischen Präzision (symbolisch) und Kreativität (neuronal)

## Operationale Regeln
- L1 Primat der Logik ( P1,P2,P3,P6)
- L2 Targeted Interrogation ( P2,P7)
- L3 Empirie vor Annahme ( P6,P3)
- L4 RootCause Correction ( P4,P6)
- L5 SystemMetareflexion ( P5)
- L6 Härtung ( P4,P5,P6)

## Messmodelle & Begründungspfade
- HarmHumanProb(a): probabilistische Risikobewertung (Kontextwahrscheinlichkeiten  Schwere  Exposition). MonteCarlo  10000 Läufe empfohlen; im HotPath ggf. Approximation + Caching.
- SustainIndex(a): normierter Nachhaltigkeitsindex [0..1] (UNSDGabgeleitet).
- Universalizable(a): regelbasierter/ symbolischer Prüfer (Katalog universalisierbarer Muster + Ableitung via Symbolik). Ergebnis als Bool + Begründungspfad.
- RiskExceptionJustified(a): dedizierter Beweisstring (These, Evidenzquellen, Vergleich geringeres Übel), formale Prüfung durch symbolische Ebene. Kein Override bei ExternalIllegal.

## Integration in HexBackend (Port 5001)
- PolicyGuard Service (empfohlen):
  - Eingabe: ActionKontext (Typ, Parameter, Operator, Evidenzlinks)
  - Ausgabe: { allowed: bool, gate: "default|override|deny", reasons: [], metrics: { harm_prob, sustain_index }, policy_version, decision_id }
  - Zeitbudget: max 150ms (inkl. Caching)
- Durchsetzungspunkte:
  - Vor kritischen Aktionen (z.B. Engines, sensitives Logging, WriteOps)
  - MCPTools (auch readonly) liefern die gleichen PolicyMetadaten im Footer
- AntwortAnreicherung (REST/MCP):
  - Header: `X-Policy-Version`, `X-Decision-Id`
  - BodyFootnote: `policy: {version, gate, allowed, reasons}`

## Performanz & Robustheit
- Caching: Key = (ActionSignature, ContextHash, PolicyHash), TTL anwendungsabhängig.
- Timeouts: SMTCheck  50ms, RiskSchätzung  80ms, Gesamt  150ms; bei Timeout  `deny` + AuditHinweis.
- Degradierung: Nur readonly Aktionen dürfen bei PolicyDegradation fortgeführt werden (mit WarnFlag), WriteOps strikt `deny`.

## Audit & Compliance
- Appendonly Log mit HashKette; Felder: timestamp, operator_id, co_operator_id, decision, justification, evidence_refs, risk_assessment_ref, policy_version, decision_id, req_id.
- Retention  10 Jahre; AuditorAPI readonly.

## Governance & Versionierung
- PolicyVersion (z.B. v2.2) in jeder Entscheidung mitspeichern.
- Migration: neue Versionen in Staging mit A/BVergleich; Breaking Changes dokumentieren.
- TestSuite: Positiv/Negativfälle (SAT/UNSAT), Grenzwerte (0.001/0.85), OverrideSzenarien, ExternalIllegal.

## MCPBezug (ReadOnly MVP)
- Tools spiegeln die gleichen Strukturen wie REST (Äquivalenztests Pflicht).
- SecurityFirst: Auth, RateLimit, BudgetGates; PolicyMetadaten im ToolErgebnis.

## MinimalCheckliste (Implementierung)
1) PolicyGuard laden (JSON) + PolicyHash berechnen
2) Messmodelle initialisieren (Risikomodul; ggf. ApproxTabellen vorladen)
3) UniversalizablePrüfer (Regelkatalog + Symbolik) aktivieren
4) SMTQuickCheck vorbereiten (Z3/Timeout/Cache)
5) REST/MCPInterceptor mit Header/BodyAnreicherung
6) AuditLogger (HashKette) anschließen
7) Tests: SAT/UNSAT, Grenzwerte, Override, ExternalIllegal, TimeoutDeny

## Anhang: Mapping JSON  SMT
- harm_prob_max = 0.001, sustain_min = 0.85 (JSON.external_frameworks.harm_thresholds)
- Universalizable / ExternallyLegal / OperatorOverride / PeerReviewed / OverrideDocProvided / RiskExceptionJustified  1:1 zu SMTPrädikaten
- Allowed entspricht der formalen Gleichung unter Formale Kernlogik


Diese Datei ist die operativ wirksame Auslegung der Verfassung v2.2. Sie minimiert ethisches/legales Risiko durch strenge DefaultGates, gewährleistet nachvollziehbare Overrides und bleibt unter realistischen Latenzbudgets auditierbar.
