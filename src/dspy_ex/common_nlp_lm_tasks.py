import dspy
from dspy_utils import (
    TextCompletion,
    SummarizeText,
    SummarizeTextAndExtractKeyTheme,
    TranslateText,
    TextTransformationAndCorrection,
    TextCorrection,
    GenerateJSON,
    ClassifyEmotion,
    TextCategorizationAndSentimentAnalsysis,
    TranslateTextToLanguage,
    SimpleAndComplexReasoning,
    WordMathProblem,
    BOLD_BEGIN,
    BOLD_END,
)

ollama_mistral = dspy.OllamaLocal(model="mistral", max_tokens=2500)
dspy.settings.configure(lm=ollama_mistral)

MODEL = "ollama/mistral"
print(f"Using MODEL={MODEL}; base=localhost")

PROMPTS = [
    "On cold winter nights, the wolves in Siberia ...",
    "On the day Franklin Benjamin realized his passion for printer, ...",
    "During the final World Cup 1998 when France beat Brazil in Paris, ...",
    "Issac Newton set under a tree when an apple fell...",
]

print("NLP Task 1: Text Generation and Completion")
# Create an instance module Predict with Signature TextCompletion
complete = dspy.Predict(TextCompletion)
# loop over all prompts
for prompt in PROMPTS:
    response = complete(in_text=prompt)
    print(f"{BOLD_BEGIN}Prompt:{BOLD_END}")
    print(prompt)
    print(f"{BOLD_BEGIN}Completion: {BOLD_END}")
    print(response.out_text)
    print("-------------------")
