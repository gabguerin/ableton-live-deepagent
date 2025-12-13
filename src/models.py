"""Models for the Ableton Producer Agent."""

from pydantic import BaseModel, Field


class Note(BaseModel):
    """A MIDI note with timing, pitch, and dynamics information."""

    pitch: int = Field(
        description="MIDI pitch number (0-127). Middle C (C4) = 60, A4 = 69. "
                   "For drums: Kick=36, Snare=38, Closed Hi-Hat=42, Open Hi-Hat=46, etc. "
                   "Chromatic scale: C=0, C#=1, D=2, D#=3, E=4, F=5, F#=6, G=7, G#=8, A=9, A#=10, B=11 (mod 12)",
        ge=0, le=127
    )

    start_time: float = Field(
        description="Start position in beats from the beginning of the clip. "
                   "In 4/4 time: 0.0=downbeat, 1.0=beat 2, 2.0=beat 3, 3.0=beat 4. "
                   "Subdivisions: 0.5=eighth note, 0.25=sixteenth note, 0.333=eighth triplet. "
                   "Can be off-grid for humanization and syncopation (e.g., 0.125, 1.75, 2.833)",
        ge=0.0
    )

    duration: float = Field(
        description="Note length in beats. In 4/4 time: 4.0=whole note, 2.0=half note, "
                   "1.0=quarter note, 0.5=eighth note, 0.25=sixteenth note. "
                   "For drums: typically 0.1-0.5 beats. For sustained notes: 1.0+ beats. "
                   "Triplets: 0.667=quarter triplet, 0.333=eighth triplet",
        gt=0.0
    )

    velocity: int = Field(
        description="Note velocity/dynamics (1-127). Controls volume and impact. "
                   "Typical ranges: ppp=10-20, pp=20-35, p=35-50, mp=50-65, mf=65-80, "
                   "f=80-95, ff=95-110, fff=110-127. "
                   "For drums: Kick=90-127, Snare=80-120, Hi-Hat=50-80, Ghost notes=20-40. "
                   "Use varied velocities for realistic dynamics and groove",
        ge=1, le=127
    )

    mute: bool = Field(
        description="Whether the note is muted (silenced). Usually False for active notes. "
                   "Set to True for notes that should be present in the MIDI data but not played",
        default=False
    )


class AddNotesArgs(BaseModel):
    """Arguments for adding MIDI notes to a specific clip in Ableton Live."""

    track_index: int = Field(
        description="The zero-based index of the track containing the clip. "
                   "Track 0 is the first track, track 1 is the second, etc. "
                   "Use get_session_info or get_track_info to find available tracks.",
        ge=0
    )

    clip_index: int = Field(
        description="The zero-based index of the clip slot in the track. "
                   "Clip slot 0 is the first slot, clip slot 1 is the second, etc. "
                   "The clip must already exist in this slot (use create_clip first if needed).",
        ge=0
    )

    notes: list[Note] = Field(
        description="List of Note objects to add to the clip. Each Note must have "
                   "pitch (0-127), start_time (beats), duration (beats), velocity (1-127), and mute (bool). "
                   "Example: [Note(pitch=60, start_time=0.0, duration=1.0, velocity=80, mute=False)]",
        min_length=1
    )
