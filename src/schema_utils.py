"""Schema utilities for dynamic model access in agents.

This module provides utilities for extracting and formatting pydantic model schemas
in a format suitable for agent consumption, enabling dynamic access to current
model definitions without hardcoding them in prompts.
"""

from src.models import Note


def get_note_schema_for_agent() -> str:
    """Extract Note model schema formatted for agent consumption.

    Returns:
        Formatted string containing Note model field descriptions,
        examples, and practical guidance for musical composition.
    """
    schema = Note.model_json_schema()

    # Extract field information
    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])
    description = schema.get("description", "")

    # Build formatted schema text for agents
    formatted_schema = f"""## Note Model Reference

{description}

### Required Fields

All Note objects must include these fields:
"""

    for field_name in required_fields:
        if field_name in properties:
            field_info = properties[field_name]
            field_desc = field_info.get("description", "")
            field_type = field_info.get("type", "unknown")

            # Add constraints info
            constraints = []
            if "minimum" in field_info:
                constraints.append(f"min: {field_info['minimum']}")
            if "maximum" in field_info:
                constraints.append(f"max: {field_info['maximum']}")
            if "exclusiveMinimum" in field_info:
                constraints.append(f"> {field_info['exclusiveMinimum']}")

            constraint_text = f" ({', '.join(constraints)})" if constraints else ""

            formatted_schema += f"""
**{field_name}** ({field_type}{constraint_text}):
{field_desc}
"""

    # Add optional fields
    optional_fields = [field for field in properties if field not in required_fields]
    if optional_fields:
        formatted_schema += "\n### Optional Fields\n"
        for field_name in optional_fields:
            if field_name in properties:
                field_info = properties[field_name]
                field_desc = field_info.get("description", "")
                field_type = field_info.get("type", "unknown")
                default_val = field_info.get("default", "N/A")

                formatted_schema += f"""
**{field_name}** ({field_type}, default: {default_val}):
{field_desc}
"""

    # Add practical examples
    formatted_schema += """

### Practical Examples

#### Basic Quarter Note:
```python
Note(pitch=60, start_time=0.0, duration=1.0, velocity=80, mute=False)
# Middle C, on the downbeat, quarter note length, moderate dynamics
```

#### Syncopated Off-Beat Note:
```python
Note(pitch=67, start_time=0.75, duration=0.5, velocity=75, mute=False)
# G4, syncopated (3/4 beat), eighth note, slightly soft dynamics
```

#### Drum Hit:
```python
Note(pitch=36, start_time=0.0, duration=0.2, velocity=110, mute=False)
# Kick drum, on the beat, short duration, loud dynamics
```

#### Triplet Timing:
```python
Note(pitch=72, start_time=0.667, duration=0.333, velocity=70, mute=False)
# C5, triplet timing (2nd note of triplet), triplet duration
```

### Usage Guidelines

- **Always specify all required fields** when creating Note objects
- **Use appropriate pitch ranges** for different instruments (see field descriptions)
- **Consider musical context** when setting velocity and timing
- **Use realistic durations** for the musical style and instrument
- **Leave mute=False** unless specifically creating muted notes for arrangement purposes

**Important**: Create Note objects directly - do not format them as tool arguments. The producer agent will handle tool formatting when calling Ableton Live functions.
"""

    return formatted_schema


def format_schema_for_prompt_injection(schema_text: str) -> str:
    """Format schema text for clean injection into prompt templates.

    Args:
        schema_text: Raw schema text to format

    Returns:
        Formatted text suitable for prompt injection
    """
    # Clean up any extra whitespace and ensure consistent formatting
    lines = schema_text.strip().split('\n')
    cleaned_lines = []

    for line in lines:
        # Preserve code blocks and headers, clean up regular text
        if line.strip().startswith('```') or line.strip().startswith('#'):
            cleaned_lines.append(line)
        else:
            cleaned_lines.append(line.rstrip())

    return '\n'.join(cleaned_lines)


def get_formatted_note_schema() -> str:
    """Get the Note model schema formatted and ready for prompt injection.

    Returns:
        Clean, formatted Note schema text ready for use in agent prompts.
    """
    raw_schema = get_note_schema_for_agent()
    return format_schema_for_prompt_injection(raw_schema)