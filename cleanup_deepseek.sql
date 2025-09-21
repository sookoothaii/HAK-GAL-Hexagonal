-- DeepSeek Validierung Cleanup
-- 10 fehlerhafte Fakten

BEGIN TRANSACTION;

-- API(AI, GraphQL, REST, TCP/IP)
DELETE FROM facts WHERE statement = 'API(AI, GraphQL, REST, TCP/IP)';
INSERT INTO facts (statement) VALUES ('API_Technologies(AI, GraphQL, REST) und Network_Protocol(TCP/IP)');

-- API(AI, GraphQL, blockchain, cloud, server)
DELETE FROM facts WHERE statement = 'API(AI, GraphQL, blockchain, cloud, server)';
INSERT INTO facts (statement) VALUES ('Computing_Concepts(AI, GraphQL, blockchain, cloud_computing, server_architecture)');

-- API(AI, HTTP, GraphQL, NoSQL, SQL)
DELETE FROM facts WHERE statement = 'API(AI, HTTP, GraphQL, NoSQL, SQL)';
INSERT INTO facts (statement) VALUES ('Web_Technologies(HTTP, GraphQL) und Data_Management(NoSQL, SQL) und Research_Field(AI)');

-- API(AI, HTTP, GraphQL, cloud, REST)
DELETE FROM facts WHERE statement = 'API(AI, HTTP, GraphQL, cloud, REST)';
INSERT INTO facts (statement) VALUES ('API_Styles(REST, GraphQL) und Protocol(HTTP) und Deployment_Model(cloud) und Technology_Field(AI)');

-- API(AI, HTTP, SQL, NoSQL, server)
DELETE FROM facts WHERE statement = 'API(AI, HTTP, SQL, NoSQL, server)';
INSERT INTO facts (statement) VALUES ('Database_Systems(SQL, NoSQL) und Protocol(HTTP) and Infrastructure(server) und Field(AI)');

-- ConsistsOf(NH3, oxygen)
DELETE FROM facts WHERE statement = 'ConsistsOf(NH3, oxygen)';
INSERT INTO facts (statement) VALUES ('ConsistsOf(NH3, nitrogen, hydrogen)');

-- ConsistsOf(H2O, carbon)
DELETE FROM facts WHERE statement = 'ConsistsOf(H2O, carbon)';
INSERT INTO facts (statement) VALUES ('ConsistsOf(H2O, hydrogen, oxygen)');

-- HasProperty(algorithm, complex)
DELETE FROM facts WHERE statement = 'HasProperty(algorithm, complex)';
INSERT INTO facts (statement) VALUES ('HasComplexity(algorithm, time_complexity, space_complexity)');

-- HasProperty(quantum, uncertain)
DELETE FROM facts WHERE statement = 'HasProperty(quantum, uncertain)';
INSERT INTO facts (statement) VALUES ('HasProperty(quantum_particles, uncertainty_principle)');

-- API(blockchain, distributed, ledger)
DELETE FROM facts WHERE statement = 'API(blockchain, distributed, ledger)';
INSERT INTO facts (statement) VALUES ('IsTypeOf(blockchain, distributed_ledger_technology)');

COMMIT;
