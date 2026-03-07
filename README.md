# gpt-cli

A conversational, autonomous CLI agent powered by OpenAI's `o3-mini` (or your choice of model). It functions as a software engineering assistant, capable of reading/writing files, running shell commands, searching the web, and creating skills.

## Features

- **Autonomous Tool Use:** The AI can plan and execute complex tasks (e.g., write a Python script, run it, and analyze the results).
- **File System Operations:** Read files, write files, and list directories safely.
- **Shell Command Execution:** Run any shell command directly from the chat.
- **Skill System:** Tell the AI to "remember" a workflow, and it will create a reusable skill file in `~/.gpt-cli/skills`.
- **Global Availability:** Install it globally and use it from any directory.

### Installation

#### Unix-like (macOS/Linux)
1. Clone this repository:
   ```bash
   git clone https://github.com/husw725/gpt-cli.git
   cd gpt-cli
   ```
2. Set up the virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Install the CLI globally:
   ```bash
   ./setup_gpt_cli.sh
   ```

#### Windows
1. Clone this repository:
   ```bash
   git clone https://github.com/husw725/gpt-cli.git
   cd gpt-cli
   ```
2. Set up the virtual environment and install dependencies:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Run the setup script for instructions on adding to PATH:
   ```cmd
   setup_gpt_cli.bat
   ```

### Usage

Start the CLI from any folder:

```bash
gpt-cli chat "What files are in this folder?"
```

Or start an interactive session:

```bash
gpt-cli chat
```

## Configuration

On first run, the CLI will prompt you for your OpenAI API Key.
This key, along with your custom skills, is securely stored in:
`~/.gpt-cli/`
