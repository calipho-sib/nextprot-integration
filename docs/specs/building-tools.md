# Building tools required for external source integration

This is a flow to build scripts, apps and libs coming from base code git repo np_loaders (needed for executing integration).
The following tasks run once and anytime base code changed.

    np_loaders_repo = nextprot-loaders
    perl_parsers_repo = nextprot-perl-parsers

        A ........ update_repos_flow(np_loaders_repo, perl_parsers_repo)
        │
        B ........ check_deployed_code
        │
        C
         `── D ... build_integration_code
         │
         └── E ... build_np_mappings_jar_code

    repo=/work/projects/integration/nextprot-loaders
    A. add update_repo_task(repo) -> updated
    B. add check_deployed_code_task -> to_build
    C. add build_code_flow

    Output produced by a task is consumed by the next

####update_repos_flow
    1. add update_repo_task np_loaders_repo -> store it in backend
    2. add update_repo_task perl_parsers_repo -> store it in backend
    provides: updated1 or updated2

####update_repo_task
    requires: [repo_path]
    execute:
        cd repo_path
        git checkout develop; git pull
    revert:
        None
    provides: updated

####check_deployed_code_task (B)
    requires: [repo_updated, [exe_file1, ..., exe_filen]]
    execute:
        if repo_updated
            return test non existence of all exe_files
        return True
    provides: to_build

###build_code_flow (C)

    repo=/work/projects/integration/nextprot-loaders
    1. add build_integration_code_task -> store it in backend
    2. add build_np_mappings_code_task -> store it in backend

####build_integration_code_task (D)
    # build and deploy parser perl code and jars libs into the FS (see special ENVs for target paths)
    requires: [to_build, PROP_FILE]
    execute:
        if to_build:
            cd /work/projects/integration/nextprot-loaders/tools.integration
            ant -lib lib/ -propertyfile PROP_FILE install-code
            mvn package
    revert:
        ?
    provides: [exe_file1, ..., exe_filen] or file glob regexp

####build_np_mappings_jar_code_task (E)
    # build and deploy code (task ant) into the FS (see special ENVs for target paths)
    requires: [to_build, PROP_FILE]
    execute:
        if to_build:
            cd /work/projects/integration/nextprot-loaders/tools.np_mappings
            ant -lib lib/ -propertyfile $PROP_FILE install-jar
    revert:
        ?
    provides: [exe_file1, ..., exe_filen] or file glob regexp



