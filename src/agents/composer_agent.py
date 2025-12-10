"""Composer Agent for Ableton Live Producer Agent."""

from typing import List, Literal, Optional

from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field, field_validator


class TimeSignature(BaseModel):
    numerator: int = Field(..., description="Beats per bar (e.g., 4)")
    denominator: int = Field(
        ..., description="Note value of one beat (e.g., 4 for quarter note)"
    )


class DrumTrack(BaseModel):
    name: str = Field(
        ...,
        description="Ableton instrument rack name, e.g., 'Kick', 'Snare', 'Closed Hihat'",
    )
    hits: List[int] = Field(
        ...,
        description="List of 16th-note grid positions where this drum hits (1-16 for a 1-bar loop)",
    )
    velocity: int = Field(
        100, ge=0, le=127, description="Global velocity for this drum part"
    )


class DrumPattern(BaseModel):
    description: str = Field(
        ..., description="Short vibe description, e.g., 'Aggressive Trap Beat'"
    )
    tempo: int = Field(..., ge=60, le=200)
    length_in_bars: int = Field(1, description="Usually 1 or 2 bars for loops")
    tracks: List[DrumTrack]


class ChordEvent(BaseModel):
    root: str = Field(..., description="Root note, e.g., 'C', 'F#', 'Bb'")
    quality: Literal["major", "minor", "maj7", "min7", "dom7", "dim", "aug"] = Field(
        ..., description="Chord quality"
    )
    extensions: Optional[List[int]] = Field(
        default=[], description="Added intervals like 9, 11, 13"
    )
    start_beat: float = Field(
        ..., description="Start time in beats (1.0 = start of bar)"
    )
    duration: float = Field(..., description="Duration in beats (4.0 = 1 full bar)")
    velocity: int = Field(90, ge=0, le=127)


class ChordProgression(BaseModel):
    key: str = Field(..., description="Musical key, e.g., 'C Minor'")
    scale: Literal[
        "major", "minor", "dorian", "phrygian", "lydian", "mixolydian", "locrian"
    ]
    tempo: int = Field(..., ge=40, le=250)
    chords: List[ChordEvent]

    @field_validator("chords")
    def sort_chords(cls, v):
        return sorted(v, key=lambda x: x.start_beat)


class BassNote(BaseModel):
    degree: int = Field(
        ...,
        description="Scale degree (1=Root, 3=Third, 5=Fifth). Use 1 for the main root note.",
    )
    octave_offset: int = Field(
        -1,
        ge=-2,
        le=2,
        description="Relative octave. -1 is standard sub/bass range, 0 is higher.",
    )
    start_beat: float = Field(
        ..., description="Start time in beats (1.0 = start of bar)"
    )
    duration: float = Field(
        ..., description="Duration in beats (0.25 = 16th note, 1.0 = quarter note)"
    )
    velocity: int = Field(
        110, ge=0, le=127, description="Bass usually needs consistent, high velocity"
    )
    glide: bool = Field(
        False,
        description="If True, slide into the next note (Simulates legato/portamento)",
    )


class BassPattern(BaseModel):
    sound_design: Literal["Sub", "Pluck", "Reese", "Acid", "Upright"] = Field(
        ..., description="Type of bass patch to load"
    )
    complexity: Literal["Simple Root", "Rhythmic", "Melodic"] = Field("Simple Root")
    notes: List[BassNote]

    @field_validator("notes")
    def sort_notes(cls, v):
        return sorted(v, key=lambda x: x.start_beat)


class MusicIdea(BaseModel):
    thought_process: str = Field(
        ...,
        description="Reasoning for how the bass locks with the drums and supports the chords",
    )
    tempo: int = Field(..., ge=60, le=180)
    key_root: str = Field(..., description="Global Key Root, e.g. 'C', 'F#'")
    key_scale: Literal["major", "minor"] = Field(..., description="Global Scale")

    drums: Optional["DrumPattern"] = None
    harmony: Optional["ChordProgression"] = None
    bass: Optional[BassPattern] = None


def get_composer_agent() -> CompiledStateGraph:
    """Return the system prompt for the Composer Agent."""
    return create_agent(
        model="gpt-5-mini",
        system_prompt="You are a Composer Agent specialized in generating structured music ideas for Ableton Live projects.",
        response_format=MusicIdea,
    )
