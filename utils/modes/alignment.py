from abc import abstractmethod


class Alignment:
    @abstractmethod
    def __str__(self):
        return NotImplementedError

    @abstractmethod
    def get_characters(self):
        return NotImplementedError

    @abstractmethod
    def project(self, revised_target_line: str, character_alignment):
        raise NotImplementedError
