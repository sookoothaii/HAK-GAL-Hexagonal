# Bulk Import Endpoint für HAK_GAL Backend

Der `/api/facts/bulk` Endpoint fehlt im Backend. Hier ist die Implementation:

## Fügen Sie diese Funktion in `hexagonal_api_enhanced_clean.py` ein:

```python
@self.app.route('/api/facts/bulk', methods=['POST'])
def bulk_insert_facts():
    """POST /api/facts/bulk - Bulk insert multiple facts"""
    data = request.get_json(silent=True) or {}
    
    statements = data.get('statements', [])
    if not statements or not isinstance(statements, list):
        return jsonify({'error': 'Missing or invalid statements array'}), 400
    
    results = {
        'inserted': 0,
        'errors': [],
        'statements': len(statements)
    }
    
    for statement in statements:
        if not isinstance(statement, str) or not statement.strip():
            results['errors'].append(f"Invalid statement: {statement}")
            continue
            
        try:
            # Parse and validate the statement
            parsed = self.fact_parser.parse(statement.strip())
            if not parsed:
                results['errors'].append(f"Failed to parse: {statement}")
                continue
            
            # Check for duplicates
            existing = self.fact_repository.find_by_statement(parsed['statement'])
            if existing:
                results['errors'].append(f"Duplicate: {statement}")
                continue
            
            # Create new fact
            fact = self.fact_service.create_fact(
                parsed['statement'],
                context={'source': 'bulk_import', 'timestamp': time.time()}
            )
            
            if fact:
                results['inserted'] += 1
                
                # Broadcast update
                self.websocket_adapter.broadcast_kb_update({
                    'action': 'fact_added',
                    'fact': fact.to_dict(),
                    'metrics': self._get_kb_metrics()
                })
            else:
                results['errors'].append(f"Failed to insert: {statement}")
                
        except Exception as e:
            results['errors'].append(f"Error with '{statement}': {str(e)}")
    
    # Log bulk import
    print(f"[BULK IMPORT] Inserted: {results['inserted']}/{len(statements)}, Errors: {len(results['errors'])}")
    
    return jsonify(results), 200 if results['inserted'] > 0 else 400
```

## Wo einfügen?

Suchen Sie nach der `add_fact()` Funktion (ca. Zeile 270) und fügen Sie die neue Funktion direkt danach ein.

## Alternative: Backend Endpoint Extension

Erstellen Sie eine neue Datei `bulk_import_extension.py`:

```python
def add_bulk_import_endpoint(app, fact_service, fact_repository, fact_parser, websocket_adapter):
    """Add bulk import endpoint to existing app"""
    
    @app.route('/api/facts/bulk', methods=['POST', 'OPTIONS'])
    def bulk_import():
        # OPTIONS for CORS preflight
        if request.method == 'OPTIONS':
            return '', 204
            
        # Implementation wie oben...
        
    print("[OK] Bulk import endpoint added: POST /api/facts/bulk")
```

Und fügen Sie in `hexagonal_api_enhanced_clean.py` nach der API-Initialisierung hinzu:

```python
# Nach Zeile ~1200 wo die anderen Extensions geladen werden:
from bulk_import_extension import add_bulk_import_endpoint
add_bulk_import_endpoint(self.app, self.fact_service, self.fact_repository, self.fact_parser, self.websocket_adapter)
```

## Test des Endpoints

```bash
curl -X POST http://localhost:8088/api/facts/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "statements": [
      "TestEntity(HasProperty, Value1).",
      "TestEntity(HasFeature, Value2)."
    ]
  }'
```

## Erwartete Antwort

```json
{
  "inserted": 2,
  "errors": [],
  "statements": 2
}
```
