from enum import Enum

class ConversionError(str, Enum):
    STORAGE_UPLOAD_FAILED = "storage_upload_failed"
    STORAGE_DOWNLOAD_FAILED = "storage_download_failed"
    NO_AUDIO_STREAM = "no_audio_stream"
    FFMPEG_FAILED = "ffmpeg_failed"
    UNSUPPORTED_FORMAT = "unsupported_format"
    UNKNOWN_ERROR = "unknown_error"
    OUTPUT_NOT_FOUND = "output_not_found"