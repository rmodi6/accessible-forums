from enum import Enum


class Label(Enum):
    Accessibility = "Accessibility"
    Usability = "Usability"
    Clarify = "Clarify"
    Description = "Description"
    Answer = "Answer"
    Suggestion = "Suggestion"
    Positive = "Positive"
    Negate = "Negate"
    Explaination = "Explaination"
    Misc = "Misc"
    Vague = "Vague"

    @staticmethod
    def question_types():
        return {Label.Accessibility, Label.Usability, Label.Clarify}
