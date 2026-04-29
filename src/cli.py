import cmd
import sys
from typing import List, Optional
from .controller import ApplicationController
from .command_parser import CommandParser, CommandParsingError
from .storage import JSONStorage
from .task_model import Task

class TodoListCLI(cmd.Cmd):
    """Command-line interface for the To-Do List application"""
    intro = "Welcome to the To-Do List CLI. Type help or ? to list commands.\n"
    prompt = "(todo) "
    
    def __init__(self):
        super().__init__()
        self.storage = JSONStorage("tasks.json")
        self.controller = ApplicationController(self.storage)
        self.command_parser = CommandParser()

    def do_add(self, arg: str) -> None:
        """Add a new task: add <title> [--description <description>]"""
        try:
            command = self.command_parser.parse(f"add {arg}")
            result = self.controller.execute_command(command)
            print(f"✅ Task added successfully (ID: {result['task_id']})\n")
        except CommandParsingError as e:
            print(f"❌ Command error: {str(e)}\n")
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")

    def do_list(self, arg: str) -> None:
        """List tasks: list [--filter <status>]"""
        try:
            command = self.command_parser.parse(f"list {arg}")
            result = self.controller.execute_command(command)
            
            if result["total"] == 0:
                print("No tasks found.\n")
                return
            
            filter_status = result.get("filter_status")
            if filter_status:
                print(f"\nFiltering tasks by status: {filter_status}\n")
            
            print(f"Total tasks: {result['total']}\n")
            print("{:<10} {:<30} {:<15} {:<20}".format("ID", "Title", "Status", "Created At"))
            print("-" * 80)
            
            for task in result["tasks"]:
                status_colors = {
                    "Pending": "🟡",
                    "In Progress": "🔵",
                    "Completed": "🟢"
                }
                status = status_colors.get(task.status, "⚪") + " " + task.status
                
                print("{:<10} {:<30} {:<15} {:<20}".format(
                    task.id[:8],  # Shorten ID for display
                    task.title[:25] + ("..." if len(task.title) > 25 else ""),
                    status,
                    task.created_at.strftime("%Y-%m-%d %H:%M")
                ))
                
                # Display description if available
                if task.description:
                    print(f"    Description: {task.description[:60]}..." if len(task.description) > 60 
                          else f"    Description: {task.description}")
                
            print()
            
        except CommandParsingError as e:
            print(f"❌ Command error: {str(e)}\n")
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")

    def do_edit(self, arg: str) -> None:
        """Edit a task: edit <id> [--title <title>] [--description <description>] [--status <status>]"""
        try:
            command = self.command_parser.parse(f"edit {arg}")
            result = self.controller.execute_command(command)
            print(f"✅ Task {result['task_id']} updated successfully\n")
            
            # Show the changes made
            changes = {k: v for k, v in result['changes'].items() if v is not None}
            if changes:
                print("Changes made:")
                for key, value in changes.items():
                    print(f"- {key.capitalize()}: {value}")
                print()
            
        except CommandParsingError as e:
            print(f"❌ Command error: {str(e)}\n")
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")

    def do_delete(self, arg: str) -> None:
        """Delete a task: delete <id>"""
        try:
            # Confirm deletion
            if not arg.strip():
                print("Error: Task ID is required\n")
                return
            
            task_id = arg.strip()
            task = self.controller.get_task_by_id(task_id)
            
            if not task:
                print(f"❌ Task {task_id} not found\n")
                return
            
            print(f"⚠️  Are you sure you want to delete task '{task.title}'? (y/N)")
            confirm = input().strip().lower()
            
            if confirm != "y":
                print("Operation cancelled\n")
                return
            
            command = self.command_parser.parse(f"delete {arg}")
            result = self.controller.execute_command(command)
            print(f"✅ {result['message']}\n")
            
        except CommandParsingError as e:
            print(f"❌ Command error: {str(e)}\n")
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")

    def do_search(self, arg: str) -> None:
        """Search tasks by title or description: search <query>"""
        if not arg.strip():
            print("Error: Search query is required\n")
            return
            
        try:
            query = arg.strip().lower()
            results = []
            
            for task in self.controller.tasks:
                if query in task.title.lower() or (task.description and query in task.description.lower()):
                    results.append(task)
            
            if not results:
                print(f"No tasks found matching '{query}'\n")
                return
            
            print(f"Found {len(results)} matching task(s):\n")
            print("{:<10} {:<30} {:<15} {:<20}".format("ID", "Title", "Status", "Created At"))
            print("-" * 80)
            
            for task in results:
                status_colors = {
                    "Pending": "🟡",
                    "In Progress": "🔵",
                    "Completed": "🟢"
                }
                status = status_colors.get(task.status, "⚪") + " " + task.status
                
                print("{:<10} {:<30} {:<15} {:<20}".format(
                    task.id[:8],  # Shorten ID for display
                    task.title[:25] + ("..." if len(task.title) > 25 else ""),
                    status,
                    task.created_at.strftime("%Y-%m-%d %H:%M")
                ))
                
                # Display description if available
                if task.description:
                    print(f"    Description: {task.description[:60]}..." if len(task.description) > 60 
                          else f"    Description: {task.description}")
                
            print()
            
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")

    def do_exit(self, arg: str) -> None:
        """Exit the application"""
        print("Goodbye!\n")
        sys.exit(0)

    def do_quit(self, arg: str) -> None:
        """Exit the application"""
        self.do_exit(arg)

    def default(self, line: str) -> None:
        """Handle unknown commands"""
        print(f"❌ Unknown command: {line.split()[0]}\nType 'help' to see available commands.\n")

    def emptyline(self) -> None:
        """Do nothing on empty input line"""
        pass

    def precmd(self, line: str) -> str:
        """Handle command prefix processing"""
        if not line.strip():
            return line
            
        # Handle multi-word commands with quotes
        try:
            parts = line.split(maxsplit=1)
            if len(parts) > 1:
                cmd, arg = parts
                # Convert command to lowercase for case-insensitive matching
                return f"{cmd.lower()} {arg}"
            else:
                return line.lower()
        except Exception:
            return line

    def do_help(self, arg: str) -> None:
        """List available commands with their help text."""
        if arg:
            # Specific command help requested
            super().do_help(arg)
        else:
            print("\nAvailable commands:")
            print("-------------------")
            print("add <title> [--description <description>]  - Add a new task")
            print("list [--filter <status>]                  - List all tasks")
            print("edit <id> [--title <title>] [--description <description>] [--status <status>]  - Edit a task")
            print("delete <id>                               - Delete a task")
            print("search <query>                            - Search tasks by title/description")
            print("help [command]                            - Show this help or command-specific help")
            print("exit/quit                                 - Exit the application\n")
            print("Status colors:")
            print("🟡 Pending | 🔵 In Progress | 🟢 Completed\n")


def main():
    """Main entry point for the application"""
    cli = TodoListCLI()
    print("Welcome to the To-Do List CLI Application!")
    print("Type 'help' to see available commands.\n")
    
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()