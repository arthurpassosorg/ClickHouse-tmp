LATEST_VERSION=$(curl -s https://packages.clickhouse.com/tgz/stable/ | \
    grep -Eo '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | sort -V -r | head -n 1)
export LATEST_VERSION
curl -O "https://packages.clickhouse.com/tgz/stable/clickhouse-common-static-$LATEST_VERSION.tgz"
curl -O "https://packages.clickhouse.com/tgz/stable/clickhouse-common-static-dbg-$LATEST_VERSION.tgz"
curl -O "https://packages.clickhouse.com/tgz/stable/clickhouse-server-$LATEST_VERSION.tgz"
curl -O "https://packages.clickhouse.com/tgz/stable/clickhouse-client-$LATEST_VERSION.tgz"

tar -xzvf "clickhouse-common-static-$LATEST_VERSION.tgz"
sudo "clickhouse-common-static-$LATEST_VERSION/install/doinst.sh"

tar -xzvf "clickhouse-common-static-dbg-$LATEST_VERSION.tgz"
sudo "clickhouse-common-static-dbg-$LATEST_VERSION/install/doinst.sh"

tar -xzvf "clickhouse-server-$LATEST_VERSION.tgz"
sudo "clickhouse-server-$LATEST_VERSION/install/doinst.sh"
sudo /etc/init.d/clickhouse-server start

tar -xzvf "clickhouse-client-$LATEST_VERSION.tgz"
sudo "clickhouse-client-$LATEST_VERSION/install/doinst.sh"
