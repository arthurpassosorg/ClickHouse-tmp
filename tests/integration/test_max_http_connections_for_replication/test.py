import time
from multiprocessing.dummy import Pool

import pytest
from helpers.cluster import ClickHouseCluster
from helpers.test_tools import assert_eq_with_retry


def _fill_nodes(nodes, shard, connections_count):
    for node in nodes:
        node.query(
            """
                CREATE DATABASE test;

                CREATE TABLE test_table(date Date, id UInt32, dummy UInt32)
                ENGINE = ReplicatedMergeTree('/clickhouse/tables/test{shard}/replicated', '{replica}')
                PARTITION BY date
                ORDER BY id
                SETTINGS
                    replicated_max_parallel_fetches_for_host={connections},
                    index_granularity=8192;
            """.format(
                shard=shard, replica=node.name, connections=connections_count
            )
        )


cluster = ClickHouseCluster(__file__)
node1 = cluster.add_instance(
    "node1",
    user_configs=[],
    main_configs=["configs/remote_servers.xml"],
    with_zookeeper=True,
)
node2 = cluster.add_instance(
    "node2",
    user_configs=[],
    main_configs=["configs/remote_servers.xml"],
    with_zookeeper=True,
)


@pytest.fixture(scope="module")
def start_small_cluster():
    try:
        cluster.start()

        _fill_nodes([node1, node2], 1, 1)

        yield cluster

    finally:
        cluster.shutdown()


def test_single_endpoint_connections_count(start_small_cluster):
    node1.query("TRUNCATE TABLE test_table")
    node2.query("SYSTEM SYNC REPLICA test_table")

    def task(count):
        print(("Inserting ten times from {}".format(count)))
        for i in range(count, count + 10):
            node1.query("insert into test_table values ('2017-06-16', {}, 0)".format(i))

    p = Pool(10)
    p.map(task, range(0, 100, 10))

    assert_eq_with_retry(node1, "select count() from test_table", "100")
    assert_eq_with_retry(node2, "select count() from test_table", "100")

    assert (
        node2.query(
            "SELECT value FROM system.events where event='CreatedHTTPConnections'"
        )
        == "1\n"
    )


def test_keepalive_timeout(start_small_cluster):
    node1.query("TRUNCATE TABLE test_table")
    node2.query("SYSTEM SYNC REPLICA test_table")

    node1.query("insert into test_table values ('2017-06-16', 777, 0)")
    assert_eq_with_retry(node2, "select count() from test_table", str(1))
    # Server keepAliveTimeout is 3 seconds, default client session timeout is 8
    # lets sleep in that interval
    time.sleep(4)

    node1.query("insert into test_table values ('2017-06-16', 888, 0)")

    time.sleep(3)

    assert_eq_with_retry(node2, "select count() from test_table", str(2))

    assert not node2.contains_in_log(
        "No message received"
    ), "Found 'No message received' in clickhouse-server.log"


node3 = cluster.add_instance(
    "node3",
    user_configs=[],
    main_configs=["configs/remote_servers.xml"],
    with_zookeeper=True,
)
node4 = cluster.add_instance(
    "node4",
    user_configs=[],
    main_configs=["configs/remote_servers.xml"],
    with_zookeeper=True,
)
node5 = cluster.add_instance(
    "node5",
    user_configs=[],
    main_configs=["configs/remote_servers.xml"],
    with_zookeeper=True,
)


@pytest.fixture(scope="module")
def start_big_cluster():
    try:
        cluster.start()

        _fill_nodes([node3, node4, node5], 2, 2)

        yield cluster

    finally:
        cluster.shutdown()


def test_multiple_endpoint_connections_count(start_big_cluster):
    def task(count):
        print(("Inserting ten times from {}".format(count)))
        if (count / 10) % 2 == 1:
            node = node3
        else:
            node = node4

        for i in range(count, count + 10):
            node.query("insert into test_table values ('2017-06-16', {}, 0)".format(i))

    p = Pool(10)
    p.map(task, range(0, 100, 10))

    assert_eq_with_retry(node3, "select count() from test_table", "100")
    assert_eq_with_retry(node4, "select count() from test_table", "100")
    assert_eq_with_retry(node5, "select count() from test_table", "100")

    # Two per each host or sometimes less, if fetches are not performed in parallel. But not more.
    assert (
        node5.query(
            "SELECT value FROM system.events where event='CreatedHTTPConnections'"
        )
        <= "4\n"
    )
