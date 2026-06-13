"""
Modell tanítása / újratanítása.

Használat:
  python train.py

Mikor kell újratanítani:
  - Új tanítóadatokat adtál hozzá (python sms_receiver.py /label endpoint)
  - Sokat változott a data/training_data.csv
"""

from categorizer import train

if __name__ == "__main__":
    print("Modell tanítása...")
    train()
    print("Kész.")
