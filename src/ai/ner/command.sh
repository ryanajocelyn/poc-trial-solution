python -m spacy init config config.cfg --lang en --pipeline ner --optimize efficiency

python -m spacy train config.cfg --output .\src\ai\ner\train\ --paths.train .\src\ai\ner\train.spacy --paths.dev .\src\ai\ner\train.spacy

python -m spacy train config.cfg --output .\train\ --paths.train .\train.spacy --paths.dev .\train.spacy