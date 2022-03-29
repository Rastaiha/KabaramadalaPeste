# KabaramadalaPeste

## Instalation

- `git clone https://github.com/Rastaiha/KabaramadalaPeste`
- `virtualenv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `python3 manage.py migrate`
- `python3 manage.py createsuperuser`
- `python3 manage.py runserver`


## Initial commands

- `python3 manage.py import_game_data`
  - inits islands, challenges & ...
  - initializtion files are in "initial_data" folder
- `python3 manage.py init_pis`
  - add all questions before running this command
  - inits participants status & assigns questions to them
- `python3 manage.py add_new_peste [Island_Id]`
  - Islands "peste"s are initialized by the "islands.csv" (when has_peste is 1, that island will have peste)
  - use this command just when you need to add additional "peste"s 

## Islands Ids
![image](https://user-images.githubusercontent.com/79265051/160621775-b4a716c4-2ecb-40cb-8d47-3617cedceb59.png)
