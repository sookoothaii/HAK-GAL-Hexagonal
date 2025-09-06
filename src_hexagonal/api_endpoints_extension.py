"""
HAK-GAL API Extension - Missing Endpoints
========================================
Adds missing /api/facts/paginated and /api/facts/stats endpoints
"""

from flask import Blueprint, jsonify, request
import time

def create_extended_endpoints(app, fact_service, fact_repository):
    """Add missing endpoints to the Flask app"""
    
    @app.route('/api/facts/paginated', methods=['GET'])
    def get_facts_paginated():
        """GET /api/facts/paginated - Paginated facts for frontend"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Validate parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 1000:
            per_page = 50
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get total count
        total_count = fact_repository.count()
        
        # Get facts with limit and offset
        try:
            if hasattr(fact_repository, 'get_paginated'):
                # Use native pagination if available
                facts = fact_repository.get_paginated(offset, per_page)
            else:
                # Fallback: get more facts and slice
                all_facts = fact_service.get_all_facts(offset + per_page)
                facts = all_facts[offset:offset + per_page]
            
            return jsonify({
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'total_pages': (total_count + per_page - 1) // per_page,
                'facts': [f.to_dict() for f in facts],
                'count': len(facts)
            })
            
        except Exception as e:
            print(f"[ERROR] Paginated facts error: {e}")
            return jsonify({
                'page': page,
                'per_page': per_page,
                'total': 0,
                'total_pages': 0,
                'facts': [],
                'count': 0,
                'error': 'Failed to fetch paginated facts'
            }), 500

    @app.route('/api/facts/stats', methods=['GET'])
    def get_facts_stats():
        """GET /api/facts/stats - Facts statistics for frontend"""
        sample_limit = request.args.get('sample_limit', 5000, type=int)
        
        try:
            # Get basic stats
            total_count = fact_repository.count()
            
            # Get sample of facts for analysis
            sample_facts = fact_service.get_all_facts(min(sample_limit, total_count))
            
            # Analyze predicates and entities
            predicates = {}
            entities = set()
            
            for fact in sample_facts:
                statement = fact.statement
                # Simple parsing: Predicate(Entity1, Entity2)
                if '(' in statement and ')' in statement:
                    pred_part = statement.split('(')[0].strip()
                    args_part = statement.split('(')[1].split(')')[0]
                    
                    # Count predicates
                    predicates[pred_part] = predicates.get(pred_part, 0) + 1
                    
                    # Extract entities
                    if ',' in args_part:
                        ent1, ent2 = [e.strip() for e in args_part.split(',', 1)]
                        entities.add(ent1)
                        entities.add(ent2)
            
            # Calculate statistics
            top_predicates = sorted(predicates.items(), key=lambda x: x[1], reverse=True)[:10]
            
            stats = {
                'total_facts': total_count,
                'sample_size': len(sample_facts),
                'unique_predicates': len(predicates),
                'unique_entities': len(entities),
                'top_predicates': [
                    {'predicate': pred, 'count': count, 'percentage': round(count/len(sample_facts)*100, 2)}
                    for pred, count in top_predicates
                ],
                'avg_facts_per_predicate': round(len(sample_facts) / len(predicates), 2) if predicates else 0,
                'sample_limit': sample_limit
            }
            
            return jsonify(stats)
            
        except Exception as e:
            print(f"[ERROR] Facts stats error: {e}")
            return jsonify({
                'total_facts': 0,
                'sample_size': 0,
                'unique_predicates': 0,
                'unique_entities': 0,
                'top_predicates': [],
                'avg_facts_per_predicate': 0,
                'sample_limit': sample_limit,
                'error': 'Failed to generate facts statistics'
            }), 500

    @app.route('/api/entities/stats', methods=['GET', 'POST', 'OPTIONS'])
    def entities_stats():
        if request.method == 'OPTIONS':
            return ('', 204)
        min_occ = request.args.get('min_occurrences', 2, type=int)
        limit = request.args.get('limit', 5000, type=int)
        try:
            # Sample facts and count entities
            entities = {}
            facts = fact_service.get_all_facts(limit)
            for f in facts:
                s = f.statement or ''
                if '(' in s and ')' in s and ',' in s:
                    args = s.split('(', 1)[1].rsplit(')', 1)[0]
                    e1, e2 = [a.strip() for a in args.split(',', 1)]
                    entities[e1] = entities.get(e1, 0) + 1
                    entities[e2] = entities.get(e2, 0) + 1
            filtered = sorted([(k, v) for k, v in entities.items() if v >= min_occ], key=lambda x: x[1], reverse=True)
            return jsonify({
                'min_occurrences': min_occ,
                'unique_entities': len(entities),
                'entities': [{'entity': k, 'count': v} for k, v in filtered]
            })
        except Exception as e:
            print(f"[ERROR] Entities stats error: {e}")
            return jsonify({'min_occurrences': min_occ, 'unique_entities': 0, 'entities': [], 'error': 'Failed to compute entities stats'}), 500

    # --- Facts update (PUT/POST) ---
    @app.route('/api/facts/update', methods=['PUT', 'POST', 'OPTIONS'])
    def update_fact():
        if _is_preflight():
            return ('', 204)
        try:
            payload = request.get_json(silent=True) or {}
            old_statement = payload.get('old_statement') or request.args.get('old_statement')
            new_statement = payload.get('new_statement') or request.args.get('new_statement')
            if not old_statement or not new_statement:
                return jsonify({'updated': 0, 'error': 'Missing old_statement/new_statement'}), 400
            updated = 0
            if hasattr(fact_repository, 'update_statement'):
                updated = int(fact_repository.update_statement(old_statement, new_statement))
            else:
                # Fallback via service if supported
                try:
                    updated = int(fact_service.update_statement(old_statement, new_statement))
                except Exception:
                    updated = 0
            return jsonify({'updated': updated})
        except Exception as e:
            print(f"[ERROR] Facts update error: {e}")
            return jsonify({'updated': 0, 'error': 'Failed to update fact'}), 500

    # --- Facts delete (POST helper for bulk_delete) ---
    @app.route('/api/facts/delete', methods=['POST', 'OPTIONS'])
    def delete_fact_post():
        if _is_preflight():
            return ('', 204)
        try:
            payload = request.get_json(silent=True) or {}
            statement = payload.get('statement') or request.args.get('statement')
            if not statement:
                return jsonify({'removed': 0, 'error': 'Missing statement'}), 400
            removed = 0
            if hasattr(fact_repository, 'delete_by_statement'):
                removed = int(fact_repository.delete_by_statement(statement))
            else:
                try:
                    removed = int(fact_service.delete_by_statement(statement))
                except Exception:
                    removed = 0
            return jsonify({'removed': removed})
        except Exception as e:
            print(f"[ERROR] Facts delete error: {e}")
            return jsonify({'removed': 0, 'error': 'Failed to delete fact'}), 500

    # New: Quality metrics endpoint (GET and POST supported; GET for frontend convenience)
    @app.route('/api/quality/metrics', methods=['GET', 'POST', 'OPTIONS'])
    def quality_metrics():
        if _is_preflight():
            return ('', 204)
        try:
            total = fact_repository.count()
            sample = fact_service.get_all_facts(min(2000, total))
            # Very simple quality heuristics as placeholder (no mocks)
            well_formed = 0
            for f in sample:
                s = f.statement or ''
                if '(' in s and ')' in s and ',' in s and s.endswith('.'):
                    well_formed += 1
            ratio = round((well_formed / len(sample)) * 100, 2) if sample else 0
            return jsonify({
                'total_facts': total,
                'sample_size': len(sample),
                'well_formed_percent': ratio
            })
        except Exception as e:
            print(f"[ERROR] Quality metrics error: {e}")
            return jsonify({'error': 'Failed to compute quality metrics'}), 500

    # New: Semantic similarity (POST)
    @app.route('/api/quality/semantic_similarity', methods=['POST', 'OPTIONS'])
    def quality_semantic_similarity():
        if _is_preflight():
            return ('', 204)
        try:
            payload = request.get_json(silent=True) or {}
            stmt = (payload.get('statement') or '').strip()
            threshold = float(payload.get('threshold', 0.8))
            limit = int(payload.get('limit', 50))
            if not stmt:
                return jsonify({'matches': [], 'error': 'Missing statement'}), 400
            # Token-basierte Jaccard-Ähnlichkeit (einfacher Platzhalter)
            def tokenize(s: str):
                return set([t.strip(" ,.'\"()") for t in s.split() if t.strip()])
            target = tokenize(stmt)
            total = fact_repository.count()
            sample = fact_service.get_all_facts(min(5000, total))
            scores = []
            for f in sample:
                s = f.statement or ''
                if not s:
                    continue
                toks = tokenize(s)
                if not toks or not target:
                    continue
                inter = len(target & toks)
                union = len(target | toks)
                sim = inter / union if union else 0.0
                if sim >= threshold:
                    scores.append({'statement': s, 'similarity': round(sim, 4)})
            scores.sort(key=lambda x: x['similarity'], reverse=True)
            return jsonify({'matches': scores[:max(1, limit)], 'threshold': threshold})
        except Exception as e:
            print(f"[ERROR] Semantic similarity error: {e}")
            return jsonify({'matches': [], 'error': 'Failed to compute similarity'}), 500

    # New: Consistency check (GET/POST)
    @app.route('/api/quality/consistency', methods=['GET', 'POST', 'OPTIONS'])
    def quality_consistency():
        if _is_preflight():
            return ('', 204)
        try:
            limit = request.args.get('limit', 100, type=int)
            total = fact_repository.count()
            sample = fact_service.get_all_facts(min(5000, total))
            # Suche nach Widersprüchen: Nicht<Pred>(args) vs <Pred>(args)
            pred_to_args = {}
            neg_pred_to_args = {}
            def parse_pred_args(s: str):
                if '(' in s and s.endswith(')'):
                    pred = s.split('(')[0].strip()
                    args = s[s.find('(')+1:-1]
                    return pred, args
                return None, None
            for f in sample:
                st = f.statement or ''
                pred, args = parse_pred_args(st)
                if not pred or args is None:
                    continue
                if pred.startswith('Nicht'):
                    base = pred[len('Nicht'):]
                    neg_pred_to_args.setdefault((base, args), []).append(st)
                else:
                    pred_to_args.setdefault((pred, args), []).append(st)
            contradictions = []
            for key, pos_list in pred_to_args.items():
                if key in neg_pred_to_args:
                    neg_list = neg_pred_to_args[key]
                    for a in pos_list:
                        for b in neg_list:
                            contradictions.append({'positive': a, 'negative': b})
                            if len(contradictions) >= limit:
                                break
                        if len(contradictions) >= limit:
                            break
                if len(contradictions) >= limit:
                    break
            return jsonify({'contradictions': contradictions, 'count': len(contradictions)})
        except Exception as e:
            print(f"[ERROR] Consistency check error: {e}")
            return jsonify({'contradictions': [], 'count': 0, 'error': 'Failed to check consistency'}), 500

    # New: Validate facts (GET/POST)
    @app.route('/api/quality/validate', methods=['GET', 'POST', 'OPTIONS'])
    def quality_validate():
        if _is_preflight():
            return ('', 204)
        try:
            limit = request.args.get('limit', 1000, type=int)
            total = fact_repository.count()
            sample = fact_service.get_all_facts(min(limit, total))
            valid = 0
            invalid = 0
            examples = []
            for f in sample:
                s = (f.statement or '').strip()
                ok = bool(s and '(' in s and s.endswith(')') and ',' in s)
                if ok:
                    valid += 1
                else:
                    invalid += 1
                    if len(examples) < 10:
                        examples.append(s)
            return jsonify({'checked': len(sample), 'valid': valid, 'invalid': invalid, 'invalid_examples': examples})
        except Exception as e:
            print(f"[ERROR] Validate facts error: {e}")
            return jsonify({'checked': 0, 'valid': 0, 'invalid': 0, 'invalid_examples': [], 'error': 'Failed to validate'}), 500

    # New: Duplicate analysis (GET)
    @app.route('/api/quality/duplicates', methods=['GET', 'OPTIONS'])
    def quality_duplicates():
        if _is_preflight():
            return ('', 204)
        try:
            threshold = request.args.get('threshold', 0.9, type=float)
            total = fact_repository.count()
            sample = fact_service.get_all_facts(min(1500, total))
            # Token-Jaccard für Duplikaterkennung (einfach, aber effektiv als Platzhalter)
            def tokens(s: str):
                return set([t.strip(" ,.'\"()") for t in s.split() if t.strip()])
            facts = [f.statement or '' for f in sample]
            tok = [tokens(s) for s in facts]
            pairs = []
            for i in range(len(facts)):
                for j in range(i+1, len(facts)):
                    a = tok[i]; b = tok[j]
                    if not a or not b:
                        continue
                    inter = len(a & b)
                    union = len(a | b)
                    sim = inter / union if union else 0.0
                    if sim >= threshold:
                        pairs.append({'statement1': facts[i], 'statement2': facts[j], 'similarity': round(sim, 4)})
                        if len(pairs) >= 200:
                            break
                if len(pairs) >= 200:
                    break
            return jsonify({'duplicate_pairs': pairs, 'threshold': threshold})
        except Exception as e:
            print(f"[ERROR] Duplicates error: {e}")
            return jsonify({'duplicate_pairs': [], 'error': 'Failed to analyze duplicates'}), 500

    # New: Top predicates endpoint (GET and POST supported)
    @app.route('/api/predicates/top', methods=['GET', 'POST', 'OPTIONS'])
    def predicates_top():
        if _is_preflight():
            return ('', 204)
        limit = _get_int('limit', 10)
        try:
            # If repository has optimized method, prefer it
            items = []
            if hasattr(fact_repository, 'predicate_counts'):
                items = fact_repository.predicate_counts(sample_limit=5000)
            else:
                sample = fact_service.get_all_facts(5000)
                counts = {}
                for f in sample:
                    s = f.statement or ''
                    if '(' in s:
                        pred = s.split('(')[0].strip()
                        if pred:
                            counts[pred] = counts.get(pred, 0) + 1
                items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            out = [{'predicate': p, 'count': c} for p, c in items[:max(1, limit)]]
            return jsonify({'top_predicates': out, 'limit': limit})
        except Exception as e:
            print(f"[ERROR] Predicates top error: {e}")
            return jsonify({'top_predicates': [], 'limit': limit, 'error': 'Failed to compute top predicates'}), 500

    def _is_preflight():
        try:
            from flask import request
            return request.method == 'OPTIONS'
        except Exception:
            return False

    def _get_int(name: str, default_val: int) -> int:
        try:
            from flask import request
            return request.args.get(name, default_val, type=int)
        except Exception:
            return default_val
    
    print("[OK] Extended API endpoints registered:")
    print("  - GET /api/facts/paginated")
    print("  - GET /api/facts/stats")
