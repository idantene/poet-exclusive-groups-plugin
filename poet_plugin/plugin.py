from cleo.events.console_events import COMMAND
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.event_dispatcher import EventDispatcher
from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.console.application import Application
from poetry.console.commands.installer_command import InstallerCommand
from poetry.core.packages.project_package import ProjectPackage


class PEGPlugin(ApplicationPlugin):
    def activate(self, application: Application):
        """Entry point for the plugin; saves the Cleo IO controller and registers the depedency remover"""
        application.event_dispatcher.add_listener(COMMAND, self.remove_dependencies)
        self.io = application._io  # noqa

    def remove_dependencies(self, event: ConsoleCommandEvent, event_name: str, dispatcher: EventDispatcher) -> None:
        """Optionally removes dependencies from the internal poetry package depending on Cleo options"""
        if not isinstance(event.command, InstallerCommand):
            return
        command: InstallerCommand = event.command
        installer = command.installer

        package: ProjectPackage = installer._package  # noqa
        only_flag = self.io.input.option('only') if self.io.input.has_option('only') else None
        without_flag = self.io.input.option('without') if self.io.input.has_option('without') else None

        if only_flag:
            package = package.with_dependency_groups(only_flag, only=True)
        if without_flag:
            package = package.without_dependency_groups(without_flag)

        command.installer._package = package
