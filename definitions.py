import dagster as dg
from dagster_dlt import DagsterDltResource

dlt_resource = DagsterDltResource()

import assets

fpl_dlt_assets = dg.load_assets_from_modules([assets])

defs = dg.Definitions(
    assets=fpl_dlt_assets,
    resources={
        "dlt": dlt_resource,
    },
)