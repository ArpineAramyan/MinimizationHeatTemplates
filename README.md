# MinimizationHeatTemplates
## О проекте
Minimization Heat Templates - проект, направленный на минимизацию набора TripleO-Heat-шаблонов. 
Также после работы программы сохраняются используемые сервисы и параметры. 
Помимо этого, программа сообщит пользователю информацию об ошибках, связанных с параметрами.
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
После этого применяется команда для установки CLI:
```commandline
python3 setup.py install
```
## Использование программы
Теперь с помощью команды ***minheat*** запускается работа программы. 
Для ознакомления с информацией о входных данных можно вызвать `help`:
```commandline
minheat -h
```
Для входных данных есть 5 параметров с соответствующими флагами:
- **templates_home** `-th` - путь до директории с шаблонами, значение по умолчанию - `'./'`;
- **minimized** `-m` - путь до директории, в которой будетт сохранён минимизированный набор шаблонов, 
значение по умолчанию - `'../minimized-heat-templates' `;
- **roles_data** `-rd` - файл, который определяет роли в overcloud и сопоставляет сервисы с каждой ролью,
значение по умолчанию - `'roles_data.yaml'`;
- **plan_env** `-pe` - файл, который содержит определения метаданных для overcloud,
значение по умолчанию - `'plan-environment.yaml'`.
- **network_data** `-nd` - файл, который содержит конфигурацию сети,
значение по умолчанию - `'networl_data.yaml'`

Помимо этого, существуют флаги, касающиеся того, что именно нужно пользователю: 
- `--parameters` - флаг, при указании которого будут напечатаны параметры;
- `--services` - флаг, при указании которого будут напечатаны сервисы;
- `--not_templates` - флаг, при указании которого будут напечатаны те файлы, которые не являются
шаблонами;
- `--param_only` - флаг, который будет применяться на минимизированном наборе для печати параметров.
