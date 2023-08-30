"""Colors and cursor escape codes functions and constants"""

# pylint: disable=C0103

import re

def fg(color_id: int = None):
    """
    Returns a foreground (text) color escape sequence
    Default: reset terminal style and color escape sequence
    
    Args:
        color_id (int): The color code ID.
    
    Returns:
        str: The ANSI escape code for the specified ID.
    """
    if color_id is None:
        color_id = "00"
    return f"\x1b[38;5;{color_id}m"

def bg(color_id: int = None):
    """
    Returns a background color escape sequence
    Default: reset terminal style and color escape sequence
    
    Args:
        color_id (int): The color code ID.
    
    Returns:
        str: The ANSI escape code for the specified ID.
    """
    if color_id is None:
        color_id = "00"
    return f"\x1b[48;5;{color_id}m"

def from_hex(hex_code: str, bg_color: bool = False):
    """
    Convert a hexadecimal color code to an ANSI escape code for color formatting.
    
    Args:
        hex_code (str): The hexadecimal color code.
        bg_color (bool, optional): Specifies if the background color should be used.
    
    Returns:
        str: The ANSI escape code for the specified color.
    """
    # Remove '#' if present
    if hex_code.startswith("#"):
        hex_code = hex_code.lstrip("#")

    # Check if the hexadecimal color code has the correct length
    if len(hex_code) != 6:
        raise ValueError("Invalid hexadecimal color code")

    # Convert hex values to integers
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)

    # Generate the ANSI escape code based on whether it's for foreground or background color
    if bg_color:
        return f"\033[48;2;{r};{g};{b}m"
    return f"\033[38;2;{r};{g};{b}m"

def from_rgb(rgb_code: str, bg_color: bool = False):
    """
    Convert an RGB color representation to an ANSI escape code for color formatting.
    
    Args:
        rgb_code (str): The RGB color representation in the formats: 
                        "rgb(r, g, b)", "rgb(r,g,b)", "(r, g, b)", "(r,g,b)".
        bg_color (bool, optional): Specifies if the background color should be used.
    
    Returns:
        str: The ANSI escape code for the specified color.
    """
    # Extract RGB values using regular expression
    pattern = r"\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)"
    match = re.match(pattern, rgb_code)
    if not match:
        raise ValueError("Invalid RGB color representation")

    # Convert extracted values to integers
    r = int(match.group(1))
    g = int(match.group(2))
    b = int(match.group(3))

    # Generate the ANSI escape code based on whether it's for foreground or background color
    if bg_color:
        return f"\033[48;2;{r};{g};{b}m"
    return f"\033[38;2;{r};{g};{b}m"

# UTILS
RMLINE = "\x1b[0G\x1b[0K"
RMALL = "\x1b[0G\x1b[0J"
CLEARSCREEN = "\x1b[0H\x1b[2J"
GOUP = "\x1b[1A"
GODOWN = "\x1b[1B"
GORIGHT = "\x1b[1C"
GOLEFT = "\x1b[1D"
# TEXT APPEARANCE
# ENABLE
BOLD = "\x1b[1m"
DIMMED = "\x1b[2m"
ITALIC = "\x1b[3m"
UNDERLINED = "\x1b[4m"
BLINK = "\x1b[5m"
INVERTCOLOR = "\x1b[7m"
HIDDEN = "\x1b[8m"
STRIKETHROUGH = "\x1b[9m"
# DISABLE ONLY...
BOLD_OFF = "\x1b[21m"
DIMMED_OFF = "\x1b[22m"
ITALIC_OFF = "\x1b[23m"
BLINK_OFF = "\x1b[25m"
UNDERLINED_OFF = "\x1b[24m"
INVERTCOLOR_OFF = "\x1b[27m"
HIDDEN_OFF = "\x1b[28m"
STRIKETHROUGH_OFF = "\x1b[29m"
# THIS RESET ALL COLORS AND STYLES.
STYLEOFF = "\x1b[00m"
COLOROFF = "\x1b[00m"
RESET = "\x1b[00m"

WARNINGFG0 = "\x1b[38;5;184m"
ERRORFG0 = "\x1b[38;5;160m"
INFOFG0 = "\x1b[38;5;6m"
SPECIAL0 = "\x1b[38;5;99m"
SPECIAL1 = "\x1b[38;5;55m"
SPECIAL2 = "\x1b[38;5;129m"
SPECIAL2 = "\x1b[38;5;135m"
