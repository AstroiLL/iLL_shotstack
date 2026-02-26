"""
Pydantic models for Shotstack Template validation.
"""

from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator


class TransitionType(str, Enum):
    """Valid transition types."""

    FADE = "fade"
    FADE_FAST = "fadeFast"
    FADE_SLOW = "fadeSlow"
    SLIDE_LEFT = "slideLeft"
    SLIDE_RIGHT = "slideRight"
    SLIDE_UP = "slideUp"
    SLIDE_DOWN = "slideDown"
    SLIDE_LEFT_FAST = "slideLeftFast"
    SLIDE_RIGHT_FAST = "slideRightFast"
    WIPE_LEFT = "wipeLeft"
    WIPE_RIGHT = "wipeRight"
    WIPE_LEFT_FAST = "wipeLeftFast"
    WIPE_RIGHT_FAST = "wipeRightFast"
    CAROUSEL_LEFT = "carouselLeft"
    CAROUSEL_RIGHT = "carouselRight"
    CAROUSEL_UP_FAST = "carouselUpFast"
    SHUFFLE_TOP_RIGHT = "shuffleTopRight"
    SHUFFLE_LEFT_BOTTOM = "shuffleLeftBottom"
    REVEAL = "reveal"
    REVEAL_FAST = "revealFast"
    REVEAL_SLOW = "revealSlow"
    ZOOM = "zoom"
    ZOOM_FAST = "zoomFast"
    ZOOM_SLOW = "zoomSlow"


class EffectType(str, Enum):
    """Valid effect types."""

    ZOOM_IN = "zoomIn"
    ZOOM_OUT = "zoomOut"
    KEN_BURNS = "kenBurns"


class FilterType(str, Enum):
    """Valid filter types."""

    BOOST = "boost"
    GREYSCALE = "greyscale"
    CONTRAST = "contrast"
    MUTED = "muted"
    NEGATIVE = "negative"
    DARKEN = "darken"
    LIGHTEN = "lighten"


class AspectRatio(str, Enum):
    """Valid aspect ratios."""

    RATIO_9_16 = "9:16"
    RATIO_16_9 = "16:9"
    RATIO_1_1 = "1:1"
    RATIO_4_5 = "4:5"
    RATIO_4_3 = "4:3"


class Asset(BaseModel):
    """Base asset model."""

    type: str

    class Config:
        extra = "allow"


class VideoAsset(Asset):
    """Video asset model."""

    type: str = "video"
    src: str
    volume: Optional[float] = Field(1.0, ge=0, le=1)

    @validator("src")
    def validate_src(cls, v):
        if not v or not v.strip():
            raise ValueError("Video src cannot be empty")
        return v


class ImageAsset(Asset):
    """Image asset model."""

    type: str = "image"
    src: str

    @validator("src")
    def validate_src(cls, v):
        if not v or not v.strip():
            raise ValueError("Image src cannot be empty")
        return v


class AudioAsset(Asset):
    """Audio asset model."""

    type: str = "audio"
    src: str
    volume: Optional[float] = Field(1.0, ge=0, le=1)

    @validator("src")
    def validate_src(cls, v):
        if not v or not v.strip():
            raise ValueError("Audio src cannot be empty")
        return v


class TextAsset(Asset):
    """Text asset model."""

    type: str = "text"
    text: str
    font: Optional[Dict[str, Any]] = None
    alignment: Optional[Dict[str, str]] = None

    @validator("text")
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Text content cannot be empty")
        return v


class Transition(BaseModel):
    """Transition model."""

    in_transition: Optional[Union[TransitionType, str]] = Field(None, alias="in")
    out: Optional[Union[TransitionType, str]] = None

    class Config:
        allow_population_by_field_name = True


class Clip(BaseModel):
    """Clip model."""

    asset: Dict[str, Any]  # Can be any asset type
    start: float
    length: float
    effect: Optional[Union[EffectType, str]] = None
    filter: Optional[Union[FilterType, str]] = None
    transition: Optional[Transition] = None

    @validator("start", "length")
    def validate_time(cls, v):
        if v < 0:
            raise ValueError("Time values must be non-negative")
        return v


class Track(BaseModel):
    """Track model."""

    clips: List[Clip]


class Timeline(BaseModel):
    """Timeline model."""

    tracks: List[Track]

    @validator("tracks")
    def validate_tracks(cls, v):
        if not v:
            raise ValueError("Timeline must have at least one track")
        return v


class Output(BaseModel):
    """Output model."""

    format: Optional[str] = "mp4"
    resolution: Optional[Dict[str, str]] = None
    aspect_ratio: Optional[Union[AspectRatio, str]] = None
    fps: Optional[float] = Field(25.0, gt=0)


class MergeEntry(BaseModel):
    """Merge array entry model."""

    find: str
    replace: str

    @validator("find")
    def validate_find(cls, v):
        if not v or not v.strip():
            raise ValueError("Find field cannot be empty")
        return v


class ShotstackTemplate(BaseModel):
    """Main Shotstack Template model."""

    template: Dict[str, Any]
    output: Output
    merge: List[MergeEntry]

    @validator("template")
    def validate_template(cls, v):
        if not v:
            raise ValueError("Template cannot be empty")

        if "timeline" not in v:
            raise ValueError("Template must contain timeline")

        # Validate timeline structure
        timeline = v["timeline"]
        if "tracks" not in timeline:
            raise ValueError("Timeline must contain tracks")

        return v

    @validator("merge")
    def validate_merge(cls, v):
        if not v:
            raise ValueError("Merge array cannot be empty")
        return v


class TemplateData(BaseModel):
    """Template-specific data model."""

    timeline: Timeline


# Asset type mapping
ASSET_MODELS = {
    "video": VideoAsset,
    "image": ImageAsset,
    "audio": AudioAsset,
    "text": TextAsset,
}
