# MinimizationHeatTemplates

## Инструкция по установке

Для начала нужно будет установить Python версии 3.6. 

Так это будет выглядеть для Ubuntu:
```commandline
sudo apt-get install python3.6
```
Для Fedora:
```commandline
sudo dnf install python3.6
```

Для облегчения работы с зависимостями рекомендуется использовать виртуальную среду. 
```commandline
python3 -m venv VIRTUALENV_HOME/minheat
source ~/minheat/bin/activate
```
Далее устанавливается файл с зависимостями:
```commandline
pip install -r requirements.txt
```
После этого применяем команду установки для CLI:
```commandline
python3 setup.py install
```
Теперь с помощью команды ***minheat*** запускается работа программы. Для ознакомления с информацией о входных данных можно сделать так:
```commandline
minheat -h
```
Для входных данных есть 4 параметра с соответствующими флагами:
- **templates_home** `-th` - путь до директории с шаблонами, значение по умолчанию - `'./'`;
- **minimized** `-m` - путь до директории, в которой будут сохранены шаблоны, оставшиеся после работы программы, значение по умолчанию - `'../minimized-heat-templates' `;
- **roles_data** `-rd` - файл, который определяет роли в overcloud и сопоставляет сервисы с каждой ролью, значение по умолчанию - `'roles_data.yaml'`
- **plan_env** `-pe` - файл, который содержит определения метаданных для overcloud, значение по умолчанию - `'plan-environment.yaml'`
