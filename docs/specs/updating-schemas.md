# Updating schemas

This is a flow to update database schemas

        A ........ update_integration_schema_task
        │
        B ........ update_np_mapping_schema_task

####update_schemas_flow
    1. add update_integration_schema_task
    2. add update_np_mapping_schema_task

####update_integration_schema_task (A)
    requires: [PROP_FILE]
    execute:
        export PROP_FILE=/work/projects/integration/nextprot-loaders/dataload.properties
        cd /work/projects/integration/nextprot-loaders/tools.integration
        ant -lib lib/ -propertyfile $PROP_FILE db-integration-update
    revert:
        None

####update_np_mapping_schema_task (B)
    requires: [PROP_FILE]
    execute:
        cd /work/projects/integration/nextprot-loaders/tools.np_mappings
        ant -lib lib/ -propertyfile $PROP_FILE db-mappings-update
    revert:
        None
