# app-ecg
An application that serves as a way to present the proof of concept of detecting ECG ST segment elevation and depression through delineation approach.

## Running
- Install all required libraries in the `requirements.txt`
- Get [LUDB v1.0.1](https://www.physionet.org/content/ludb/1.0.1/) and [models](https://drive.google.com/drive/folders/1sFgiqyl2DRwZtD_mgs7bYrrFRSSb1ObQ?usp=sharing). Code for model training and data preparation can be found [here](https://github.com/rendyisd/ecg-delineation)
- Run `initialize_database.py`
- Run `main.py`

## Acknowledgement
- [LUDB v1.0.1](https://www.physionet.org/content/ludb/1.0.1/) for the signal data used in the model training
- ISysRG, for the workstation computer used for the model training

## Screenshots
![Main](assets/screenshots/1.png "Main")
![Side panel](assets/screenshots/2.png "Side panel")
![Result - 1](assets/screenshots/3.png "Result - 1")
![Result - 2](assets/screenshots/4.png "Result - 2")
