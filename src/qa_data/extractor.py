import pandas as pd


def extract(id,dir):

    df = pd.read_csv(dir)

    transcription=df.loc[df["recording_id"] == id]["left_transcription"].to_numpy()[0]

    return transcription