# HAK/GAL Verfassung v2.2 (operationalisierte Fassung)

Diese Fassung ist die pr�zise, umsetzbare Zusammenf�hrung von JSON-Policy, SMTKernlogik und praktischen Betriebsregeln f�r den autonomen HexBackend (Port 5001) und MCPReadOnlyIntegration.

## Zielbild
- Externe Legalit�t hat Vorrang (kein Override m�glich).
- StandardGate ist streng, OverrideGate streng kontrolliert.
- Nachvollziehbare Messmodelle, deterministische Pr�fung, auditierbare Entscheidungen.

## Formale Kernlogik (Summary)
- Allowed(a) := ExternallyLegal(a)  (PassesDefaultEthic(a)  PassesOverride(a))
- PassesDefaultEthic(a) := Universalizable(a)  HarmHumanProb(a)  0.001  SustainIndex(a)  0.85
- PassesOverride(a) := OperatorOverride(a)  PeerReviewed(a)  OverrideDocProvided(a)  RiskExceptionJustified(a)
- Grenzen: 0  HarmHumanProb  1, 0  SustainIndex  1
- Externe Illegalit�t kann niemals �berschrieben werden.

## Prinzipien (P1P7, komprimiert)
- P1 Komplement�re Intelligenz: passende Aufgabenzuteilung (symbolisch/neural/menschlich)
- P2 Gezielte Befragung: pr�zise, testbare Eingaben und Metriken
- P3 Externe Verifikation: unabh�ngiger Nachweis
- P4 Bewusstes Grenz�berschreiten: diagnostische Fehler provozieren, Ursachen verstehen
- P5 SystemMetareflexion: wiederkehrende Selbstanalyse
- P6 Empirische Validierung: quantitative, reproduzierbare Evidenz
- P7 Konjugierte Zust�nde: Tradeoffs zwischen Pr�zision (symbolisch) und Kreativit�t (neuronal)

## Operationale Regeln
- L1 Primat der Logik ( P1,P2,P3,P6)
- L2 Targeted Interrogation ( P2,P7)
- L3 Empirie vor Annahme ( P6,P3)
- L4 RootCause Correction ( P4,P6)
- L5 SystemMetareflexion ( P5)
- L6 H�rtung ( P4,P5,P6)

## Messmodelle & Begr�ndungspfade
- HarmHumanProb(a): probabilistische Risikobewertung (Kontextwahrscheinlichkeiten  Schwere  Exposition). MonteCarlo  10000 L�ufe empfohlen; im HotPath ggf. Approximation + Caching.
- SustainIndex(a): normierter Nachhaltigkeitsindex [0..1] (UNSDGabgeleitet).
- Universalizable(a): regelbasierter/ symbolischer Pr�fer (Katalog universalisierbarer Muster + Ableitung via Symbolik). Ergebnis als Bool + Begr�ndungspfad.
- RiskExceptionJustified(a): dedizierter Beweisstring (These, Evidenzquellen, Vergleich geringeres �bel), formale Pr�fung durch symbolische Ebene. Kein Override bei ExternalIllegal.

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
- Caching: Key = (ActionSignature, ContextHash, PolicyHash), TTL anwendungsabh�ngig.
- Timeouts: SMTCheck  50ms, RiskSch�tzung  80ms, Gesamt  150ms; bei Timeout  `deny` + AuditHinweis.
- Degradierung: Nur readonly Aktionen d�rfen bei PolicyDegradation fortgef�hrt werden (mit WarnFlag), WriteOps strikt `deny`.

## Audit & Compliance
- Appendonly Log mit HashKette; Felder: timestamp, operator_id, co_operator_id, decision, justification, evidence_refs, risk_assessment_ref, policy_version, decision_id, req_id.
- Retention  10 Jahre; AuditorAPI readonly.

## Governance & Versionierung
- PolicyVersion (z.B. v2.2) in jeder Entscheidung mitspeichern.
- Migration: neue Versionen in Staging mit A/BVergleich; Breaking Changes dokumentieren.
- TestSuite: Positiv/Negativf�lle (SAT/UNSAT), Grenzwerte (0.001/0.85), OverrideSzenarien, ExternalIllegal.

## MCPBezug (ReadOnly MVP)
- Tools spiegeln die gleichen Strukturen wie REST (�quivalenztests Pflicht).
- SecurityFirst: Auth, RateLimit, BudgetGates; PolicyMetadaten im ToolErgebnis.

## MinimalCheckliste (Implementierung)
1) PolicyGuard laden (JSON) + PolicyHash berechnen
2) Messmodelle initialisieren (Risikomodul; ggf. ApproxTabellen vorladen)
3) UniversalizablePr�fer (Regelkatalog + Symbolik) aktivieren
4) SMTQuickCheck vorbereiten (Z3/Timeout/Cache)
5) REST/MCPInterceptor mit Header/BodyAnreicherung
6) AuditLogger (HashKette) anschlie�en
7) Tests: SAT/UNSAT, Grenzwerte, Override, ExternalIllegal, TimeoutDeny

## Anhang: Mapping JSON  SMT
- harm_prob_max = 0.001, sustain_min = 0.85 (JSON.external_frameworks.harm_thresholds)
- Universalizable / ExternallyLegal / OperatorOverride / PeerReviewed / OverrideDocProvided / RiskExceptionJustified  1:1 zu SMTPr�dikaten
- Allowed entspricht der formalen Gleichung unter Formale Kernlogik


Diese Datei ist die operativ wirksame Auslegung der Verfassung v2.2. Sie minimiert ethisches/legales Risiko durch strenge DefaultGates, gew�hrleistet nachvollziehbare Overrides und bleibt unter realistischen Latenzbudgets auditierbar.
