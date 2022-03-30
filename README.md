# KabaramadalaPeste

## Instalation

- `git clone https://github.com/Rastaiha/KabaramadalaPeste`
- `virtualenv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `python3 manage.py migrate`
- `python3 manage.py createsuperuser`
  - execute initial commands before running server...
- `python3 manage.py runserver`


## Initial commands

- `python3 manage.py create_participants`
  - Dont forget to fill `/accounts/initial_data/participants.csv` with users data
- `python3 manage.py import_game_data`
  - Dont forget to correct islands name before running command
  - Inits islands, challenges & ...
  - Initialization files are in "initial_data" folder
- `python3 manage.py init_questions`
  - Import questions from `/media/soals/Questions/Judgeable/i` (i in range(1,36))
- `python3 manage.py init_pis`
  - Add all questions before running this command
  - Inits participants' status & assigns questions to them
- `python3 manage.py add_new_peste [Island_Id]`
  - Islands "peste"s are initialized by "islands.csv" in "initial_data" folder. When "has_peste" is 1, that island will have "peste"
  - Use this command just when you need to add additional "peste"s 

## Islands Ids
![image](https://user-images.githubusercontent.com/79265051/160621775-b4a716c4-2ecb-40cb-8d47-3617cedceb59.png)
