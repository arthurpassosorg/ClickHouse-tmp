#pragma once

#include <base/shared_ptr_helper.h>
#include <Storages/System/IStorageSystemOneBlock.h>

namespace DB
{

class AsynchronousMetrics;
class Context;


/** Implements system table asynchronous_metrics, which allows to get values of periodically (asynchronously) updated metrics.
  */
class StorageSystemAsynchronousMetrics final : public shared_ptr_helper<StorageSystemAsynchronousMetrics>,
    public IStorageSystemOneBlock<StorageSystemAsynchronousMetrics>
{
    friend struct shared_ptr_helper<StorageSystemAsynchronousMetrics>;
public:
    std::string getName() const override { return "SystemAsynchronousMetrics"; }

    static NamesAndTypesList getNamesAndTypes();

private:
    const AsynchronousMetrics & async_metrics;

protected:
    StorageSystemAsynchronousMetrics(const StorageID & table_id_, const AsynchronousMetrics & async_metrics_);

    void fillData(MutableColumns & res_columns, ContextPtr context, const SelectQueryInfo & query_info) const override;
};

}
