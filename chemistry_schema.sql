-- SQLite Schema Extension for n-ary Chemical Facts
-- ==================================================

-- Haupttabelle bleibt, aber mit erweiterter Struktur
ALTER TABLE facts ADD COLUMN argument_count INTEGER DEFAULT 2;
ALTER TABLE facts ADD COLUMN argument_types TEXT; -- JSON array
ALTER TABLE facts ADD COLUMN domain TEXT DEFAULT 'general';

-- Neue Tabelle für strukturierte Argumente
CREATE TABLE IF NOT EXISTS fact_arguments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fact_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    value TEXT NOT NULL,
    type TEXT, -- 'compound', 'condition', 'value', 'identifier'
    metadata TEXT, -- JSON für SMILES, InChI, units etc.
    FOREIGN KEY (fact_id) REFERENCES facts(id),
    UNIQUE(fact_id, position)
);

-- Index für effiziente Suche
CREATE INDEX IF NOT EXISTS idx_fact_args_type ON fact_arguments(type);
CREATE INDEX IF NOT EXISTS idx_fact_domain ON facts(domain);
CREATE INDEX IF NOT EXISTS idx_fact_argcount ON facts(argument_count);

-- View für Chemistry Facts
CREATE VIEW IF NOT EXISTS chemistry_facts AS
SELECT 
    f.id,
    f.statement,
    f.argument_count,
    f.domain,
    GROUP_CONCAT(
        fa.value || COALESCE(' [' || json_extract(fa.metadata, '$.smiles') || ']', ''),
        ', '
    ) as structured_args
FROM facts f
LEFT JOIN fact_arguments fa ON f.id = fa.fact_id
WHERE f.domain = 'chemistry'
GROUP BY f.id;

-- Beispiel-Inserts
INSERT INTO facts (statement, argument_count, domain) 
VALUES ('ChemicalReaction(H2, O2, H2O)', 3, 'chemistry');

INSERT INTO fact_arguments (fact_id, position, value, type, metadata)
VALUES 
    (last_insert_rowid(), 1, 'H2', 'compound', '{"formula":"H2","smiles":"[H][H]"}'),
    (last_insert_rowid(), 2, 'O2', 'compound', '{"formula":"O2","smiles":"O=O"}'),
    (last_insert_rowid(), 3, 'H2O', 'compound', '{"formula":"H2O","smiles":"O"}');
