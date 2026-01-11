# Auth related exceptions
class UsernameAlreadyExistsException(Exception):
    pass

class UserNotFoundException(Exception):
    pass

class InvalidCredentialsException(Exception):
    pass


# Storage exceptions
class StorageError(Exception):
    pass

class ObjectNotFoundError(StorageError):
    pass

class StoragePermissionError(StorageError):
    pass

class StorageUnavailableError(StorageError):
    pass


# Conversion jobs exceptions
class ConversionJobNotFoundException(Exception):
    pass

class ConversionFailedException(Exception):
    pass

class JobNotCompletedException(Exception):
    pass
