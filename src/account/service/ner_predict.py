from transformers import pipeline


class NerPredit:
    def __init__(self, df):
        self.df = df

    def identify_entities(self):
        remarks = df["Description"].to_list()

        model_output_checkpoint = "D:\\Abiz\\Technical\\code\\python\\poc-trial-solution\\src\\ai\\ner\\transformers\\nfl_pbp_token_classifier"
        classifier = pipeline(
            "ner", model=model_output_checkpoint, aggregation_strategy="simple"
        )
        responses = classifier(remarks)
        flats = []
        ents = []
        for ind, row in enumerate(responses):
            ents_row = []
            flat = None
            for ent in row:
                if ent["entity_group"] == "FLAT":
                    flat = f"Apt-{ent['word']}"

                ents_row.append({ent["entity_group"]: ent["word"]})

            print(flat, remarks[ind], ents_row)
            flats.append(flat)
            ents.append(ents_row)
        print(ents)
        return flats
