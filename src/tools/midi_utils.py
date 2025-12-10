"""MIDI utility functions for Ableton tools."""

from typing import Union, List
from .midi_models import MidiNote, Velocity, DrumHit, ChordVoicing


def note(
    pitch: Union[int, str],
    start: float,
    duration: float = 0.25,
    velocity: Union[int, Velocity] = 100,
    muted: bool = False
) -> MidiNote:
    """Create a MIDI note with optional pitch name support.

    Args:
        pitch: MIDI pitch number (0-127) or note name like 'C4', 'F#3'
        start: Start time in beats
        duration: Duration in beats (default: 0.25 = 16th note)
        velocity: Note velocity (default: 100)
        muted: Whether note is muted (default: False)

    Returns:
        MidiNote object

    Examples:
        >>> note("C4", 0.0, 1.0, Velocity.F)
        >>> note(60, 1.0, 0.5, 110)
        >>> note("G#3", 2.0, 0.25, Velocity.MF, muted=True)
    """
    if isinstance(pitch, str):
        pitch = note_name_to_midi(pitch)

    if isinstance(velocity, Velocity):
        velocity = velocity.value

    return MidiNote(
        pitch=pitch,
        start_time=start,
        duration=duration,
        velocity=velocity,
        muted=muted
    )


def note_name_to_midi(note_name: str) -> int:
    """Convert note name like 'C4' to MIDI number.

    Args:
        note_name: Note name in format like 'C4', 'F#3', 'Bb5'

    Returns:
        MIDI note number (0-127)

    Examples:
        >>> note_name_to_midi("C4")
        60
        >>> note_name_to_midi("A4")
        69
    """
    note_map = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }

    # Parse note name and octave
    if len(note_name) < 2:
        raise ValueError(f"Invalid note name: {note_name}")

    # Handle sharp/flat notes
    if '#' in note_name or 'b' in note_name:
        note = note_name[:-1]
        octave = int(note_name[-1])
    else:
        note = note_name[:-1]
        octave = int(note_name[-1])

    if note not in note_map:
        raise ValueError(f"Invalid note: {note}")

    midi_number = note_map[note] + (octave + 1) * 12

    if not 0 <= midi_number <= 127:
        raise ValueError(f"Note {note_name} is outside MIDI range (0-127)")

    return midi_number


def midi_to_note_name(midi_number: int) -> str:
    """Convert MIDI number to note name.

    Args:
        midi_number: MIDI note number (0-127)

    Returns:
        Note name like 'C4', 'F#3'

    Examples:
        >>> midi_to_note_name(60)
        'C4'
        >>> midi_to_note_name(69)
        'A4'
    """
    if not 0 <= midi_number <= 127:
        raise ValueError(f"MIDI number must be between 0 and 127, got {midi_number}")

    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_number // 12) - 1
    note = note_names[midi_number % 12]

    return f"{note}{octave}"


def chord(
    root: Union[str, int],
    chord_type: str,
    start: float,
    duration: float = 4.0,
    velocity: Union[int, Velocity] = 80,
    inversion: int = 0
) -> List[MidiNote]:
    """Create a chord as a list of MIDI notes.

    Args:
        root: Root note as MIDI number or note name
        chord_type: Type of chord ('major', 'minor', 'maj7', etc.)
        start: Start time in beats
        duration: Duration in beats (default: 4.0)
        velocity: Chord velocity
        inversion: Chord inversion (0=root position)

    Returns:
        List of MidiNote objects forming the chord

    Examples:
        >>> chord("C4", "major", 0.0, 4.0, Velocity.MF)
        >>> chord(60, "min7", 2.0, 2.0, 90)
    """
    if isinstance(root, str):
        root = note_name_to_midi(root)

    if isinstance(velocity, Velocity):
        velocity = velocity.value

    chord_voicing = ChordVoicing(
        root_note=root,
        chord_type=chord_type,
        inversion=inversion,
        start_time=start,
        duration=duration,
        velocity=velocity
    )

    return chord_voicing.to_midi_notes()


def drum_hit(
    drum_name: str,
    midi_note: int,
    start: float,
    velocity: Union[int, Velocity] = 100
) -> MidiNote:
    """Create a drum hit as a MIDI note.

    Args:
        drum_name: Name of the drum sound
        midi_note: MIDI note number for this drum
        start: Start time in beats
        velocity: Hit velocity

    Returns:
        MidiNote object representing the drum hit

    Examples:
        >>> drum_hit("Kick", 36, 0.0, Velocity.F)
        >>> drum_hit("Snare", 38, 1.0, 110)
    """
    if isinstance(velocity, Velocity):
        velocity = velocity.value

    hit = DrumHit(
        drum_name=drum_name,
        midi_note=midi_note,
        start_time=start,
        velocity=velocity
    )

    return hit.to_midi_note()


# Common drum mappings (General MIDI standard)
DRUM_MAP = {
    "kick": 36,
    "kick_2": 35,
    "snare": 38,
    "snare_2": 40,
    "clap": 39,
    "closed_hat": 42,
    "open_hat": 46,
    "crash": 49,
    "ride": 51,
    "tom_low": 45,
    "tom_mid": 48,
    "tom_high": 50,
    "rim_shot": 37,
    "cowbell": 56,
    "shaker": 70,
}


def drum(
    drum_name: str,
    start: float,
    velocity: Union[int, Velocity] = 100
) -> MidiNote:
    """Create a drum hit using common drum names.

    Args:
        drum_name: Name of the drum (kick, snare, closed_hat, etc.)
        start: Start time in beats
        velocity: Hit velocity

    Returns:
        MidiNote object for the drum hit

    Examples:
        >>> drum("kick", 0.0, Velocity.F)
        >>> drum("snare", 1.0, 110)
        >>> drum("closed_hat", 0.5, Velocity.P)
    """
    drum_key = drum_name.lower().replace(" ", "_").replace("-", "_")

    if drum_key not in DRUM_MAP:
        available_drums = ", ".join(DRUM_MAP.keys())
        raise ValueError(f"Unknown drum: {drum_name}. Available drums: {available_drums}")

    midi_note = DRUM_MAP[drum_key]

    return drum_hit(drum_name, midi_note, start, velocity)


def pattern(notes: List[MidiNote], repeat: int = 1, offset: float = 0.0) -> List[MidiNote]:
    """Repeat a pattern of notes.

    Args:
        notes: List of MidiNote objects to repeat
        repeat: Number of times to repeat (default: 1)
        offset: Time offset for the entire pattern (default: 0.0)

    Returns:
        List of repeated notes with adjusted timing

    Examples:
        >>> kick_pattern = [drum("kick", 0.0), drum("kick", 2.0)]
        >>> repeated = pattern(kick_pattern, repeat=4, offset=0.0)
    """
    if not notes:
        return []

    # Find the duration of the original pattern
    pattern_duration = max(note.start_time + note.duration for note in notes)

    repeated_notes = []

    for rep in range(repeat):
        for note in notes:
            new_note = MidiNote(
                pitch=note.pitch,
                start_time=note.start_time + (rep * pattern_duration) + offset,
                duration=note.duration,
                velocity=note.velocity,
                muted=note.muted
            )
            repeated_notes.append(new_note)

    return repeated_notes