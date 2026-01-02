class UsernameAlreadyExistsException(Exception):
    pass

class UserNotFoundException(Exception):
    pass

class InvalidCredentialsException(Exception):
    pass

class StorageError(Exception):
    pass