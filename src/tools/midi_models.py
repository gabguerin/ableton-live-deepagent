"""MIDI data models for Ableton tools."""

from enum import IntEnum
from typing import Union
from pydantic import BaseModel, Field, validator


class Velocity(IntEnum):
    """Common velocity values for convenience."""
    SILENT = 0
    PPP = 16      # pianississimo
    PP = 32       # pianissimo
    P = 48        # piano
    MP = 64       # mezzo-piano
    MF = 80       # mezzo-forte
    F = 96        # forte
    FF = 112      # fortissimo
    FFF = 127     # fortississimo


class MidiNote(BaseModel):
    """A single MIDI note with proper validation."""

    pitch: int = Field(
        ...,
        ge=0,
        le=127,
        description="MIDI pitch (0-127, where 60=C4)"
    )
    start_time: float = Field(
        ...,
        ge=0.0,
        description="Start time in beats (0.0 = clip start)"
    )
    duration: float = Field(
        ...,
        gt=0.0,
        description="Note duration in beats (e.g., 0.25 = 16th note, 1.0 = quarter note)"
    )
    velocity: int = Field(
        100,
        ge=1,
        le=127,
        description="Note velocity (1-127, use Velocity enum for common values)"
    )
    muted: bool = Field(
        False,
        description="Whether the note is muted"
    )

    @validator('pitch')
    def validate_pitch(cls, v):
        """Validate MIDI pitch range."""
        if not 0 <= v <= 127:
            raise ValueError("MIDI pitch must be between 0 and 127")
        return v

    @validator('velocity')
    def validate_velocity(cls, v):
        """Validate MIDI velocity range."""
        if not 1 <= v <= 127:
            raise ValueError("MIDI velocity must be between 1 and 127")
        return v

    def to_ableton_dict(self) -> dict:
        """Convert to the dictionary format expected by Ableton."""
        return {
            "pitch": self.pitch,
            "start_time": self.start_time,
            "duration": self.duration,
            "velocity": self.velocity,
            "mute": self.muted
        }


class DrumHit(BaseModel):
    """A drum hit with specific drum sound and timing."""

    drum_name: str = Field(
        ...,
        description="Name of the drum sound (e.g., 'Kick', 'Snare', 'Hi-hat')"
    )
    midi_note: int = Field(
        ...,
        ge=0,
        le=127,
        description="MIDI note number for this drum sound"
    )
    start_time: float = Field(
        ...,
        ge=0.0,
        description="Start time in beats"
    )
    velocity: int = Field(
        100,
        ge=1,
        le=127,
        description="Hit velocity"
    )

    def to_midi_note(self) -> MidiNote:
        """Convert drum hit to MidiNote."""
        return MidiNote(
            pitch=self.midi_note,
            start_time=self.start_time,
            duration=0.1,  # Short duration for drum hits
            velocity=self.velocity,
            muted=False
        )


class ChordVoicing(BaseModel):
    """A chord with specific voicing and timing."""

    root_note: int = Field(..., ge=0, le=127, description="Root note MIDI number")
    chord_type: str = Field(..., description="Chord type (major, minor, maj7, etc.)")
    inversion: int = Field(0, ge=0, le=3, description="Chord inversion (0=root position)")
    start_time: float = Field(..., ge=0.0, description="Start time in beats")
    duration: float = Field(..., gt=0.0, description="Chord duration in beats")
    velocity: int = Field(80, ge=1, le=127, description="Chord velocity")

    def to_midi_notes(self) -> list[MidiNote]:
        """Convert chord to list of MidiNote objects."""
        # This would contain logic to generate chord voicings
        # For now, return a simple triad
        intervals = self._get_chord_intervals()
        notes = []

        for i, interval in enumerate(intervals):
            pitch = self.root_note + interval
            if pitch <= 127:  # Stay within MIDI range
                notes.append(MidiNote(
                    pitch=pitch,
                    start_time=self.start_time,
                    duration=self.duration,
                    velocity=self.velocity - (i * 5),  # Slightly decrease velocity for higher notes
                    muted=False
                ))

        return notes

    def _get_chord_intervals(self) -> list[int]:
        """Get chord intervals based on chord type."""
        chord_intervals = {
            "major": [0, 4, 7],
            "minor": [0, 3, 7],
            "maj7": [0, 4, 7, 11],
            "min7": [0, 3, 7, 10],
            "dom7": [0, 4, 7, 10],
            "dim": [0, 3, 6],
            "aug": [0, 4, 8],
        }

        return chord_intervals.get(self.chord_type.lower(), [0, 4, 7])