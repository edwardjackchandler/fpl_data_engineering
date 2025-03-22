from dagster import AssetExecutionContext
from dagster_dlt import DagsterDltResource, dlt_assets
from dlt import pipeline

from dlt_sources.fpl_resolve_pipeline import fpl_source


@dlt_assets(
    dlt_source=fpl_source(),
    dlt_pipeline=pipeline(
        import_schema_path="schemas/import",
        export_schema_path="schemas/export",
        pipeline_name="fpl",
        destination="duckdb",
        dataset_name="fpl_data",
        dev_mode=True,
    ),
    name="fpl",
    group_name="fpl",
)
def dagster_fpl_assets(context: AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(context=context)