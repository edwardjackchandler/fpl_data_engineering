from typing import Any, Dict, Generator, List

import dlt
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources


@dlt.source
def fpl_source():
    """Source function for fetching Fantasy Premier League data."""

    @dlt.resource(write_disposition="replace")
    def league_ids() -> Generator[List[Dict[str, Any]], None, None]:
        """A seed list of repositories to fetch"""
        yield [{"league_id": "741068"}, {"league_id": "741069"}]

    config: RESTAPIConfig = {
        "client": {"base_url": "https://fantasy.premierleague.com/api/"},
        "resource_defaults": {
            # "primary_key": "id",
            "write_disposition": "replace",
            "endpoint": {
                "params": {
                    "per_page": 100,
                },
            },
        },
        "resources": [
            {
                "name": "standings",
                "write_disposition": "merge",
                "endpoint": {
                    "path": "leagues-classic/{league_id}/standings/",
                    "params": {
                        "league_id": {
                            "type": "resolve",
                            "resource": "league_ids",
                            "field": "league_id",
                        },
                    },
                    "data_selector": "standings.results",
                },
            },
            {
                "name": "history",
                "write_disposition": "append",  # Incremental append
                "primary_key": ["_standings_entry", "event"],  # Prevent duplicates
                "endpoint": {
                    "path": "entry/{entry_id}/history/",
                    "params": {
                        "entry_id": {
                            "type": "resolve",
                            "resource": "standings",
                            "field": "entry",
                        },
                    },
                    # "data_selector": "history",
                },
                "include_from_parent": ["entry"],
            },
            {
                "name": "events",
                "write_disposition": "replace",
                "endpoint": {
                    "path": "bootstrap-static/",
                    "data_selector": "events",
                },
            },
            {
                "name": "picks",
                "write_disposition": "append",
                "endpoint": {
                    "path": "entry/{entry_id}/event/{event_id}/picks/",
                    "params": {
                        "entry_id": {
                            "type": "resolve",
                            "resource": "history",
                            "field": "_standings_entry",
                        },
                        "event_id": {
                            "type": "resolve",
                            "resource": "history",
                            "field": "event",
                        },
                    },
                    "data_selector": "picks",
                },
                "include_from_parent": ["_standings_entry", "event"],
            },
            {
                "name": "players",
                "write_disposition": "replace",  # Complete replacement
                "endpoint": {
                    "path": "bootstrap-static/",
                    "data_selector": "elements",
                },
            },
            {
                "name": "player_details",
                "write_disposition": "replace",
                "endpoint": {
                    "path": "element-summary/{element_id}/",
                    "params": {
                        "element_id": {
                            "type": "resolve",
                            "resource": "players",
                            "field": "id",
                        },
                    },
                },
                "include_from_parent": ["id", "web_name"],
            },
            league_ids(),
        ],
    }

    yield from rest_api_resources(config)


# # Create a pipeline and run it
# pipeline = dlt.pipeline(
#     import_schema_path="schemas/import",
#     export_schema_path="schemas/export",
#     pipeline_name="fpl",
#     destination="duckdb",
#     dataset_name="fpl_data",
#     dev_mode=True,
# )
