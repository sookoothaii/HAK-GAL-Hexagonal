# Snapshot Status – Read-Only (2025-08-14 14:09)

Quelle: Live-Endpoints (read-only)

## Health
```json
{"architecture":"hexagonal","port":5001,"repository":"SQLiteFactRepository","status":"operational","mojo":{"flag_enabled":false,"available":false,"backend":"python_fallback"}}
```

## Status (light)
```json
{"architecture":"hexagonal","status":"operational"}
```

## Mojo-Status
```json
{"mojo":{"present":true,"flag_enabled":false,"available":false,"backend":"python_fallback"}}
```

## Facts Count
```json
{"count":3865,"cached":true}
```

## Top Predicates (sample_limit=5000)
```json
{"top_predicates":[{"predicate":"HasPart","count":768},{"predicate":"HasPurpose","count":714},{"predicate":"Causes","count":601},{"predicate":"HasProperty","count":580},{"predicate":"IsDefinedAs","count":389},{"predicate":"IsSimilarTo","count":203},{"predicate":"IsTypeOf","count":203},{"predicate":"HasLocation","count":106},{"predicate":"ConsistsOf","count":88},{"predicate":"WasDevelopedBy","count":66}],"total_checked":3865}
```

## Quality Metrics
```json
{"total":3865,"checked":3865,"invalid":5,"duplicates":0,"isolated":1808,"contradictions":0,"top_predicates":[{"predicate":"HasPart","count":768},{"predicate":"HasPurpose","count":714},{"predicate":"Causes","count":601},{"predicate":"HasProperty","count":580},{"predicate":"IsDefinedAs","count":388},{"predicate":"IsSimilarTo","count":203},{"predicate":"IsTypeOf","count":203},{"predicate":"HasLocation","count":106},{"predicate":"ConsistsOf","count":88},{"predicate":"WasDevelopedBy","count":66}]}
```

## Hinweise
- Alle Endpunkte wurden nur lesend abgefragt; keine Schreibpfade berührt.
- Mojo ist vorbereitet, aktuell `flag_enabled=false` und `available=false` (Stub/Native kann später aktiviert werden).
