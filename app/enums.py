from enum import Enum


class Label(Enum):
    access = "Accessibility"
    use = "Usability"
    clarify = "Clarify"
    answer = "Answer"
    confirm = "Confirm"
    negate = "Negate"
    elaborate = "Elaborate"
    thank = "Thank you"
    misc = "Miscellaneous"

    @staticmethod
    def question_types():
        return {Label.access, Label.use}
