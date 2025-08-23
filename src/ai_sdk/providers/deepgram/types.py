"""Type definitions for Deepgram AI provider."""

from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field


# Deepgram Transcription Model IDs
DeepgramTranscriptionModelId = Literal[
    "base",
    "base-general",
    "base-meeting", 
    "base-phonecall",
    "base-finance",
    "base-conversationalai",
    "base-voicemail",
    "base-video",
    "enhanced",
    "enhanced-general",
    "enhanced-meeting",
    "enhanced-phonecall",
    "enhanced-finance",
    "nova",
    "nova-general",
    "nova-phonecall",
    "nova-medical",
    "nova-2",
    "nova-2-general", 
    "nova-2-meeting",
    "nova-2-phonecall",
    "nova-2-finance",
    "nova-2-conversationalai",
    "nova-2-voicemail",
    "nova-2-video",
    "nova-2-medical",
    "nova-2-drivethru",
    "nova-2-automotive",
    "nova-2-atc",
    "nova-3",
    "nova-3-general",
    "nova-3-medical",
]


class DeepgramTranscriptionAPIRequest(BaseModel):
    """Request parameters for Deepgram transcription API."""
    
    # Base parameters
    language: Optional[str] = Field(default=None, description="Language to use for transcription")
    model: Optional[str] = Field(default=None, description="Model to use for transcription")
    
    # Formatting options
    smart_format: Optional[bool] = Field(default=None, description="Use smart formatting for numbers, dates, times")
    punctuate: Optional[bool] = Field(default=None, description="Add punctuation to transcript")
    paragraphs: Optional[bool] = Field(default=None, description="Format transcript into paragraphs")
    
    # Summarization and analysis
    summarize: Optional[Union[Literal["v2"], Literal[False]]] = Field(default=None, description="Generate summary")
    topics: Optional[bool] = Field(default=None, description="Identify topics in transcript")
    intents: Optional[bool] = Field(default=None, description="Identify intents in transcript")
    sentiment: Optional[bool] = Field(default=None, description="Analyze sentiment in transcript")
    
    # Entity detection
    detect_entities: Optional[bool] = Field(default=None, description="Detect and tag named entities")
    
    # Redaction options
    redact: Optional[Union[str, List[str]]] = Field(default=None, description="Terms to redact from transcript")
    replace: Optional[str] = Field(default=None, description="String to replace redacted content")
    
    # Search and keywords
    search: Optional[str] = Field(default=None, description="Term or phrase to search for")
    keyterm: Optional[str] = Field(default=None, description="Key term to identify")
    
    # Speaker-related features
    diarize: Optional[bool] = Field(default=None, description="Identify different speakers")
    utterances: Optional[bool] = Field(default=None, description="Segment transcript into utterances")
    utt_split: Optional[float] = Field(default=None, description="Minimum silence duration to trigger new utterance")
    
    # Miscellaneous
    filler_words: Optional[bool] = Field(default=None, description="Include filler words (um, uh, etc.)")


class DeepgramTranscriptionOptions(BaseModel):
    """Provider-specific options for Deepgram transcription."""
    
    language: Optional[str] = Field(default=None, description="Language to use for transcription")
    smart_format: Optional[bool] = Field(default=None, description="Use smart formatting for numbers, dates, times")
    punctuate: Optional[bool] = Field(default=None, description="Add punctuation to transcript")
    paragraphs: Optional[bool] = Field(default=None, description="Format transcript into paragraphs")
    summarize: Optional[Union[Literal["v2"], Literal[False]]] = Field(default=None, description="Generate summary")
    topics: Optional[bool] = Field(default=None, description="Identify topics in transcript")
    intents: Optional[bool] = Field(default=None, description="Identify intents in transcript")
    sentiment: Optional[bool] = Field(default=None, description="Analyze sentiment in transcript")
    detect_entities: Optional[bool] = Field(default=None, description="Detect and tag named entities")
    redact: Optional[Union[str, List[str]]] = Field(default=None, description="Terms to redact from transcript")
    replace: Optional[str] = Field(default=None, description="String to replace redacted content")
    search: Optional[str] = Field(default=None, description="Term or phrase to search for")
    keyterm: Optional[str] = Field(default=None, description="Key term to identify")
    diarize: Optional[bool] = Field(default=None, description="Identify different speakers")
    utterances: Optional[bool] = Field(default=None, description="Segment transcript into utterances")
    utt_split: Optional[float] = Field(default=None, description="Minimum silence duration to trigger new utterance")
    filler_words: Optional[bool] = Field(default=None, description="Include filler words (um, uh, etc.)")


class DeepgramWord(BaseModel):
    """Word in Deepgram transcription response."""
    
    word: str = Field(description="Word text")
    start: float = Field(description="Start time in seconds")
    end: float = Field(description="End time in seconds")
    confidence: Optional[float] = Field(default=None, description="Confidence score")
    speaker: Optional[int] = Field(default=None, description="Speaker ID")


class DeepgramAlternative(BaseModel):
    """Alternative transcription result."""
    
    transcript: str = Field(description="Transcribed text")
    confidence: Optional[float] = Field(default=None, description="Confidence score")
    words: Optional[List[DeepgramWord]] = Field(default=None, description="Word-level details")
    paragraphs: Optional['DeepgramParagraphs'] = Field(default=None, description="Paragraph structure")
    entities: Optional[List['DeepgramEntity']] = Field(default=None, description="Named entities")
    summaries: Optional[List['DeepgramSummary']] = Field(default=None, description="Generated summaries")
    topics: Optional[List['DeepgramTopic']] = Field(default=None, description="Identified topics")
    intents: Optional[List['DeepgramIntent']] = Field(default=None, description="Identified intents")
    sentiments: Optional[List['DeepgramSentiment']] = Field(default=None, description="Sentiment analysis")


class DeepgramChannel(BaseModel):
    """Channel in Deepgram transcription response."""
    
    alternatives: List[DeepgramAlternative] = Field(description="Alternative transcriptions")
    search: Optional[List['DeepgramSearchResult']] = Field(default=None, description="Search results")


class DeepgramMetadata(BaseModel):
    """Metadata from Deepgram transcription response."""
    
    transaction_key: Optional[str] = Field(default=None, description="Transaction key")
    request_id: Optional[str] = Field(default=None, description="Request ID")
    sha256: Optional[str] = Field(default=None, description="SHA256 hash")
    created: Optional[str] = Field(default=None, description="Creation timestamp")
    duration: Optional[float] = Field(default=None, description="Audio duration in seconds")
    channels: Optional[int] = Field(default=None, description="Number of channels")
    models: Optional[List[str]] = Field(default=None, description="Models used")
    model_info: Optional[dict] = Field(default=None, description="Model information")


class DeepgramResults(BaseModel):
    """Results from Deepgram transcription."""
    
    channels: List[DeepgramChannel] = Field(description="Channel results")
    utterances: Optional[List['DeepgramUtterance']] = Field(default=None, description="Utterance segments")


class DeepgramTranscriptionResponse(BaseModel):
    """Response from Deepgram transcription API."""
    
    metadata: Optional[DeepgramMetadata] = Field(default=None, description="Response metadata")
    results: Optional[DeepgramResults] = Field(default=None, description="Transcription results")


class DeepgramParagraphs(BaseModel):
    """Paragraph structure in transcription."""
    
    transcript: str = Field(description="Full transcript")
    paragraphs: List['DeepgramParagraph'] = Field(description="Individual paragraphs")


class DeepgramParagraph(BaseModel):
    """Individual paragraph."""
    
    sentences: List['DeepgramSentence'] = Field(description="Sentences in paragraph")
    num_words: int = Field(description="Number of words")
    start: float = Field(description="Start time")
    end: float = Field(description="End time")


class DeepgramSentence(BaseModel):
    """Sentence in paragraph."""
    
    text: str = Field(description="Sentence text")
    start: float = Field(description="Start time")
    end: float = Field(description="End time")


class DeepgramEntity(BaseModel):
    """Named entity in transcription."""
    
    label: str = Field(description="Entity label/type")
    value: str = Field(description="Entity value")
    confidence: float = Field(description="Confidence score")
    start_word: int = Field(description="Start word index")
    end_word: int = Field(description="End word index")


class DeepgramSummary(BaseModel):
    """Generated summary."""
    
    summary: str = Field(description="Summary text")
    start_word: int = Field(description="Start word index")
    end_word: int = Field(description="End word index")


class DeepgramTopic(BaseModel):
    """Identified topic."""
    
    topic: str = Field(description="Topic name")
    confidence: float = Field(description="Confidence score")


class DeepgramIntent(BaseModel):
    """Identified intent."""
    
    intent: str = Field(description="Intent name")
    confidence: float = Field(description="Confidence score")


class DeepgramSentiment(BaseModel):
    """Sentiment analysis result."""
    
    sentiment: str = Field(description="Sentiment label (positive/negative/neutral)")
    confidence: float = Field(description="Confidence score")
    start_word: int = Field(description="Start word index")
    end_word: int = Field(description="End word index")


class DeepgramUtterance(BaseModel):
    """Utterance segment."""
    
    start: float = Field(description="Start time")
    end: float = Field(description="End time")
    confidence: float = Field(description="Confidence score")
    channel: int = Field(description="Channel number")
    transcript: str = Field(description="Transcript text")
    words: List[DeepgramWord] = Field(description="Words in utterance")
    speaker: Optional[int] = Field(default=None, description="Speaker ID")


class DeepgramSearchResult(BaseModel):
    """Search result in transcription."""
    
    query: str = Field(description="Search query")
    hits: List['DeepgramSearchHit'] = Field(description="Search hits")


class DeepgramSearchHit(BaseModel):
    """Search hit."""
    
    confidence: float = Field(description="Confidence score")
    start: float = Field(description="Start time")
    end: float = Field(description="End time")
    snippet: str = Field(description="Text snippet")


class DeepgramError(BaseModel):
    """Error response from Deepgram API."""
    
    error: 'DeepgramErrorDetail' = Field(description="Error details")


class DeepgramErrorDetail(BaseModel):
    """Error detail from Deepgram API."""
    
    message: str = Field(description="Error message")
    code: int = Field(description="Error code")