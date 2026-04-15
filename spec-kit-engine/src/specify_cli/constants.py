import tomllib
from pathlib import Path

def _load_branding():
    # Find pyproject.toml (works in development and editable installs)
    root = Path(__file__).parent.parent.parent
    pyproject_path = root / "pyproject.toml"
    
    # Default values
    cli_name = "specify"
    project_name = "Specify"
    tagline_ext = "Spec-Driven Development Toolkit"
    banner = """
███████╗██████╗ ███████╗ ██████╗██╗███████╗██╗   ██╗
██╔════╝██╔══██╗██╔════╝██╔════╝██║██╔════╝╚██╗ ██╔╝
███████╗██████╔╝█████╗  ██║     ██║█████╗   ╚████╔╝
╚════██║██╔═══╝ ██╔══╝  ██║     ██║██╔══╝    ╚██╔╝
███████║██║     ███████╗╚██████╗██║██║        ██║
╚══════╝╚═╝     ╚══════╝ ╚═════╝╚═╝╚═╝        ╚═╝
"""

    if pyproject_path.exists():
        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                
                # Get the first script name from [project.scripts]
                scripts = data.get("project", {}).get("scripts", {})
                if scripts:
                    cli_name = list(scripts.keys())[0]
                
                # Get branding from [tool.specify.branding]
                branding = data.get("tool", {}).get("specify", {}).get("branding", {})
                project_name = branding.get("project_name", project_name)
                tagline_ext = branding.get("tagline", tagline_ext)
                banner = branding.get("banner", banner)
        except Exception:
            pass # Fallback to defaults if error reading
            
    return cli_name, project_name, tagline_ext, banner

CLI_NAME, PROJECT_NAME, TAGLINE_EXT, BANNER = _load_branding()

# These are now derived from the values above
TAGLINE = f"GitHub {PROJECT_NAME} - {TAGLINE_EXT}"
CLI_HELP = f"Setup tool for {PROJECT_NAME} spec-driven development projects"
