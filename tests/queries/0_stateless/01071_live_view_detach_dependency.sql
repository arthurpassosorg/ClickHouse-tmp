-- Tags: no-replicated-database, no-parallel, no-fasttest

SET allow_experimental_live_view = 1;
DROP TABLE IF EXISTS test;
DROP TABLE IF EXISTS lv;
CREATE TABLE test (n Int8) ENGINE = Memory;
CREATE LIVE VIEW lv AS SELECT * FROM test;
DETACH TABLE lv;
INSERT INTO test VALUES (42);
DROP TABLE test;
ATTACH TABLE lv;
DROP TABLE lv;
