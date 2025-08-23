"""AssemblyAI provider types and data models."""

from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field

# Model identifiers
AssemblyAITranscriptionModelId = Literal["best", "nano"]

# Language codes supported by AssemblyAI
AssemblyAILanguageCode = Literal[
    "en", "en_au", "en_uk", "en_us", "es", "fr", "de", "it", "pt", "nl",
    "af", "sq", "am", "ar", "hy", "as", "az", "ba", "eu", "be", "bn", "bs",
    "br", "bg", "my", "ca", "zh", "hr", "cs", "da", "et", "fo", "fi", "gl",
    "ka", "el", "gu", "ht", "ha", "haw", "he", "hi", "hu", "is", "id", "ja",
    "jw", "kn", "kk", "km", "ko", "lo", "la", "lv", "ln", "lt", "lb", "mk",
    "mg", "ms", "ml", "mt", "mi", "mr", "mn", "ne", "no", "nn", "oc", "pa",
    "ps", "fa", "pl", "ro", "ru", "sa", "sr", "sn", "sd", "si", "sk", "sl",
    "so", "su", "sw", "sv", "tl", "tg", "ta", "tt", "te", "th", "bo", "tr",
    "tk", "uk", "ur", "uz", "vi", "cy", "yi", "yo"
]

# PII redaction policies
PIIRedactionPolicy = Literal[
    "account_number", "banking_information", "blood_type", "credit_card_cvv",
    "credit_card_expiration", "credit_card_number", "date", "date_interval",
    "date_of_birth", "drivers_license", "drug", "duration", "email_address",
    "event", "filename", "gender_sexuality", "healthcare_number", "injury",
    "ip_address", "language", "location", "marital_status", "medical_condition",
    "medical_process", "money_amount", "nationality", "number_sequence",
    "occupation", "organization", "passport_number", "password", "person_age",
    "person_name", "phone_number", "physical_attribute", "political_affiliation",
    "religion", "statistics", "time", "url", "us_social_security_number",
    "username", "vehicle_id", "zodiac_sign"
]

class CustomSpellingRule(BaseModel):
    """Custom spelling rule for transcription."""
    from_words: List[str] = Field(alias="from")
    to_word: str = Field(alias="to")

class AssemblyAITranscriptionSettings(BaseModel):
    """AssemblyAI transcription call settings."""
    # Audio processing settings
    audio_end_at: Optional[int] = Field(None, description="End time of audio in milliseconds")
    audio_start_from: Optional[int] = Field(None, description="Start time of audio in milliseconds")
    
    # Feature toggles
    auto_chapters: Optional[bool] = Field(None, description="Enable Auto Chapters")
    auto_highlights: Optional[bool] = Field(None, description="Enable Key Phrases")
    content_safety: Optional[bool] = Field(None, description="Enable Content Moderation")
    disfluencies: Optional[bool] = Field(None, description="Transcribe filler words")
    entity_detection: Optional[bool] = Field(None, description="Enable Entity Detection")
    filter_profanity: Optional[bool] = Field(None, description="Filter profanity")
    format_text: Optional[bool] = Field(None, description="Enable text formatting")
    iab_categories: Optional[bool] = Field(None, description="Enable Topic Detection")
    language_detection: Optional[bool] = Field(None, description="Enable automatic language detection")
    multichannel: Optional[bool] = Field(None, description="Enable multichannel transcription")
    punctuate: Optional[bool] = Field(None, description="Enable automatic punctuation")
    sentiment_analysis: Optional[bool] = Field(None, description="Enable sentiment analysis")
    speaker_labels: Optional[bool] = Field(None, description="Enable speaker diarization")
    summarization: Optional[bool] = Field(None, description="Enable summarization")
    
    # Configuration values
    boost_param: Optional[Literal["low", "default", "high"]] = Field(None, description="Word boost level")
    content_safety_confidence: Optional[int] = Field(None, ge=25, le=100, description="Content safety confidence threshold")
    language_code: Optional[AssemblyAILanguageCode] = Field(None, description="Language code")
    language_confidence_threshold: Optional[float] = Field(None, description="Language confidence threshold")
    speakers_expected: Optional[int] = Field(None, description="Expected number of speakers")
    speech_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Speech detection threshold")
    
    # Custom settings
    custom_spelling: Optional[List[CustomSpellingRule]] = Field(None, description="Custom spelling rules")
    word_boost: Optional[List[str]] = Field(None, description="Words to boost recognition for")
    topics: Optional[List[str]] = Field(None, description="Topics to identify")
    
    # PII redaction settings
    redact_pii: Optional[bool] = Field(None, description="Redact PII from transcript")
    redact_pii_audio: Optional[bool] = Field(None, description="Generate redacted audio")
    redact_pii_audio_quality: Optional[Literal["mp3", "wav"]] = Field(None, description="Redacted audio format")
    redact_pii_policies: Optional[List[PIIRedactionPolicy]] = Field(None, description="PII redaction policies")
    redact_pii_sub: Optional[Literal["entity_name", "hash"]] = Field(None, description="PII replacement method")
    
    # Summarization settings
    summary_model: Optional[Literal["informative", "conversational", "catchy"]] = Field(None, description="Summary model")
    summary_type: Optional[Literal["bullets", "bullets_verbose", "gist", "headline", "paragraph"]] = Field(None, description="Summary type")
    
    # Webhook settings
    webhook_url: Optional[str] = Field(None, description="Webhook URL")
    webhook_auth_header_name: Optional[str] = Field(None, description="Webhook auth header name")
    webhook_auth_header_value: Optional[str] = Field(None, description="Webhook auth header value")

class AssemblyAIProviderSettings(BaseModel):
    """AssemblyAI provider configuration."""
    api_key: Optional[str] = Field(None, description="API key for authentication")
    base_url: str = Field("https://api.assemblyai.com", description="Base API URL")
    headers: Optional[Dict[str, str]] = Field(None, description="Additional headers")

class AssemblyAIUploadResponse(BaseModel):
    """Response from upload endpoint."""
    upload_url: str

class AssemblyAIWordTimestamp(BaseModel):
    """Word timestamp information."""
    text: str
    start: float
    end: float

class AssemblyAITranscriptionResponse(BaseModel):
    """Response from transcription endpoint."""
    text: Optional[str] = None
    language_code: Optional[str] = None
    words: Optional[List[AssemblyAIWordTimestamp]] = None
    audio_duration: Optional[float] = None

class AssemblyAIErrorDetail(BaseModel):
    """AssemblyAI error detail."""
    message: str
    code: int

class AssemblyAIError(BaseModel):
    """AssemblyAI error response."""
    error: AssemblyAIErrorDetail