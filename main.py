import os
import json
import typer
import subprocess
from rich.console import Console
from rich.markdown import Markdown
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv, set_key
from duckduckgo_search import DDGS

app = typer.Typer(help="A conversational GPT CLI with Tool Use and Skills")
console = Console()

# --- Configuration ---
CONFIG_DIR = Path.home() / ".gpt-cli"
ENV_FILE = CONFIG_DIR / "config.env"
SKILLS_DIR = CONFIG_DIR / "skills"

# Ensure base directories exist
CONFIG_DIR.mkdir(exist_ok=True)
SKILLS_DIR.mkdir(exist_ok=True)

# Load environment variables
load_dotenv(ENV_FILE)

# --- Tool Functions ---

def run_shell_command(command: str) -> str:
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=False
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        return output if output.strip() else "Command executed successfully with no output."
    except Exception as e:
        return f"Error executing command: {str(e)}"

def read_file(file_path: str) -> str:
    """Read contents of a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(file_path: str, content: str) -> str:
    """Write contents to a file."""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def list_directory(dir_path: str) -> str:
    """Lists the names of files and subdirectories directly within a specified directory path."""
    try:
        path = Path(dir_path)
        if not path.is_dir():
            return f"Error: {dir_path} is not a valid directory."
        
        entries = sorted(os.listdir(path))
        return "\n".join(entries) if entries else "(Empty directory)"
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def web_search(query: str) -> str:
    """Perform a web search using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No results found."
        return "\n\n".join([f"Title: {r['title']}\nURL: {r['href']}\nBody: {r['body']}" for r in results])
    except Exception as e:
        return f"Error searching web: {str(e)}"

def create_skill(name: str, description: str, instructions: str) -> str:
    """
    Creates and saves a new skill that the AI can use in subsequent sessions.
    """
    skill_file = SKILLS_DIR / f"{name.replace(' ', '_').lower()}.md"
    content = f"""# {name}

## Description
{description}

## Instructions
{instructions}
"""
    try:
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Skill '{name}' created successfully. It is now available for use."
    except Exception as e:
        return f"Error creating skill: {str(e)}"

# --- Tool Mapping and Schema ---

TOOLS_MAP = {
    "run_shell_command": run_shell_command,
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "web_search": web_search,
    "create_skill": create_skill,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Run a shell command on the user's local machine.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string", "description": "The bash command to execute."}},
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a local file.",
            "parameters": {
                "type": "object",
                "properties": {"file_path": {"type": "string", "description": "Absolute or relative path to the file."}},
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Writes the complete content to a file. Overwrites existing files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file."},
                    "content": {"type": "string", "description": "The complete content to write."}
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "Lists the names of files and subdirectories directly within a specified directory path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dir_path": {"type": "string", "description": "The path to the directory to list."}
                },
                "required": ["dir_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The search query."}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_skill",
            "description": "Saves a new skill for the AI. Use this when the user asks you to remember something, learn a new workflow, or create a new capability for yourself.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "A short, descriptive name for the skill."},
                    "description": {"type": "string", "description": "A one-sentence explanation of what the skill does."},
                    "instructions": {"type": "string", "description": "Detailed, step-by-step instructions for the AI to follow."}
                },
                "required": ["name", "description", "instructions"]
            }
        }
    }
]

# --- Skill Loading ---

def load_skills() -> str:
    """Load all skills into a prompt string."""
    skills_text = ""
    skills = list(SKILLS_DIR.glob("*.md"))
    if skills:
        skills_text += "\n\n--- AVAILABLE SKILLS ---\n"
        for s in skills:
            with open(s, "r", encoding="utf-8") as f:
                skills_text += f"\n<skill name='{s.stem}'>\n{f.read()}\n</skill>\n"
    return skills_text

# --- Main Chat Application ---

def _run_agent_loop(client: OpenAI, messages: list):
    """Core loop for tool-using agent."""
    with console.status("[bold green]Thinking...[/bold green]", spinner="dots"):
        while True:
            response = client.chat.completions.create(
                model="gpt-5.2",
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
            )
            message = response.choices[0].message
            messages.append(message)

            if message.content:
                console.print(Markdown(message.content))

            if not message.tool_calls:
                break # End of turn

            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                    console.print(f"[dim]Running tool: {func_name} with {args}[/dim]")
                    
                    if func_name in TOOLS_MAP:
                        result = TOOLS_MAP[func_name](**args)
                    else:
                        result = f"Error: Tool '{func_name}' not found."
                except json.JSONDecodeError:
                    result = f"Error: Invalid arguments for tool '{func_name}'."
                except Exception as e:
                    result = f"Error executing tool '{func_name}': {e}"

                # Truncate result if it's too long
                if len(result) > 10000:
                    result = result[:10000] + "... [Truncated]"
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

def ensure_api_key():
    """Check for API key and prompt user if not found."""
    if os.getenv("OPENAI_API_KEY"):
        return True
    
    console.print("[bold yellow]OpenAI API Key not found.[/bold yellow]")
    console.print("Please enter your API key to continue. It will be saved to a local config file.")
    
    while True:
        api_key = console.input("[bold]API Key:[/bold] ", password=True)
        if api_key.strip():
            # Ensure the .env file exists before setting the key
            ENV_FILE.touch(exist_ok=True)
            set_key(str(ENV_FILE), "OPENAI_API_KEY", api_key)
            os.environ["OPENAI_API_KEY"] = api_key
            console.print(f"[green]API Key saved to {ENV_FILE}. You can start chatting now.[/green]")
            return True
        else:
            console.print("[red]API Key cannot be empty. Please try again.[/red]")

@app.command(name="chat")
def chat_command(prompt: str = typer.Argument(None, help="The initial prompt to start the chat.")):
    """Start an interactive chat with your AI assistant."""
    if not ensure_api_key():
        raise typer.Exit()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = """You are gpt-cli, a fully autonomous software engineering agent.
CRITICAL MANDATES:
1. NEVER ASK THE USER TO DO SOMETHING YOU CAN DO YOURSELF. If a file path is fuzzy, use `run_shell_command` with `find . -iname "*fuzzy*"` or `grep` to locate it autonomously. Do not ask the user for the path.
2. ZERO-CLICK EXECUTION: When writing a script or fixing a bug, YOU MUST execute it yourself using `run_shell_command`. NEVER just show the code and ask the user to run it or modify it. Write it, run it, and present the final output.
3. ITERATIVE FIXING: If an error occurs during your tool execution (e.g., script fails, file not found), YOU MUST autonomously diagnose, fix the script/command, and re-run it until it succeeds. DO NOT stop and ask the user to fix it.
4. You have tools to read/write files, list directories, run shell commands, search the web, and create skills. Use them relentlessly to achieve the user's goal without manual intervention.
"""
    system_prompt += load_skills()

    messages = [{"role": "system", "content": system_prompt}]

    if prompt:
        console.print(f"\n[bold blue]You:[/bold blue] {prompt}")
        messages.append({"role": "user", "content": prompt})
        _run_agent_loop(client, messages)

    while True:
        try:
            user_input = console.input("\n[bold blue]You:[/bold blue] ")
            if user_input.lower() in ("exit", "quit", "q"):
                break
            if not user_input.strip():
                continue
            
            # Print user message to ensure we log it (though console.input already shows the prompt)
            messages.append({"role": "user", "content": user_input})
            _run_agent_loop(client, messages)

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold]Goodbye![/bold]")
            break

if __name__ == "__main__":
    app()
