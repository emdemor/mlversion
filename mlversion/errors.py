class ExistingVersionError(Exception):
    pass


class ExistingAttributeError(Exception):
    def __init__(self, object, attribute_name):
        message = f"Attribute {attribute_name} already exists in object " f"of the class {object.__class__}."
        super().__init__(message)


class IncompatibleArgumentsError(Exception):
    pass


class IncompatibleArtifactTypeError(Exception):
    def __init__(self, expected_type, local_type):
        message = f"Local artifact type {local_type} is incompatible with " f"the expected type {expected_type}."
        super().__init__(message)
