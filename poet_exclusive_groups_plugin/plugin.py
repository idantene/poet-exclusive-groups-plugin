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

        available_groups = set(package.dependency_group_names(include_optional=True))
        desired_groups = available_groups.copy()
        if self.io.input.option('only-root') is True:
            package = package.with_dependency_groups(['main'], only=True)
        if self.io.input.option('no-dev') is True:
            package = package.without_dependency_groups(['dev'])
        if self.io.input.option('only'):
            package = package.with_dependency_groups(self.io.input.option('only'), only=True)
        if self.io.input.option('without'):
            package = package.without_dependency_groups(self.io.input.option('without'))

        command.installer._package = package.with_dependency_groups(desired_groups)
