import sqlite3

conn = sqlite3.connect('../hexagonal_kb.db')
cursor = conn.cursor()

# Machine Learning Facts
cursor.execute('SELECT statement FROM facts WHERE statement LIKE "%MachineLearning%" LIMIT 8')
ml_facts = cursor.fetchall()
print('=== MACHINE LEARNING FACTS ===')
for fact in ml_facts:
    print(f'• {fact[0]}')

# Philosophie Facts  
cursor.execute('SELECT statement FROM facts WHERE statement LIKE "%Kant%" LIMIT 6')
phil_facts = cursor.fetchall()
print('\n=== PHILOSOPHIE FACTS ===')
for fact in phil_facts:
    print(f'• {fact[0]}')

# Wissenschaft Facts
cursor.execute('SELECT statement FROM facts WHERE statement LIKE "%Causes%" LIMIT 6')
science_facts = cursor.fetchall()
print('\n=== KASUALITÄT FACTS ===')
for fact in science_facts:
    print(f'• {fact[0]}')

# Komplexe Facts mit mehreren Konzepten
cursor.execute('SELECT statement FROM facts WHERE LENGTH(statement) > 80 ORDER BY LENGTH(statement) DESC LIMIT 5')
complex_facts = cursor.fetchall()
print('\n=== KOMPLEXE FACTS ===')
for fact in complex_facts:
    print(f'• {fact[0]}')

conn.close()

