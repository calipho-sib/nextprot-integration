

class CodeBuilder:
    """Build perl scripts, libs and java apps
    """
    def __init__(self, workflow):
        self.__workflow = workflow

    def build_integration_perl(self):
        self.__workflow.exec_ant_task(self.__workflow.get_tools_integration_dir(), 'install-perl')

    def build_integration_jars(self):
        self.__workflow.exec_ant_task(self.__workflow.get_tools_integration_dir(), 'install-jars')

    def build_np_mappings_jar(self):
        self.__workflow.exec_ant_task(self.__workflow.get_tools_mappings_dir(), 'install-jar')
