import sys
import requests
#  Первое задание - Количество задач в колонках реализовано в функции read()
#  Второе задание - Создание колонки реализовано в функции create_column(),
#  чтобы проверить пишем в консоль python D1-homework create_column 'Новая колонка'
#  Третье задание - Проверка повторов в названии заданий реализовано в функции check_replays()
#  проверка происходит после метода read() и create_task(),
#  но можно проверить отдельно в консоли функцией check_replays()
#  В функции create_task() если указать несуществующую колонку, то она создастся автоматически
#  Вместо функции move() используется собственный метод delete(), но суть та же(используется ID)

base_url = "https://api.trello.com/1/{}"
auth_params = {
    'key': "Ваш ключ",
    'token': "Ваш токен", }
board_id = "Ваш ID доски"


def read():
    # Получим данные всех колонок на доске:
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:
    for column in column_data:
        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        task_number = len(task_data)
        print(column['name'], ',', 'Задач: ', task_number)
        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t' + task['name'] + " - " + task['id'])


def create_task(task_name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна
    for column in column_data:
        if column['name'] == column_name:
            # Создадим задачу с именем _name_ в найденной колонке
            requests.post(base_url.format('cards'), data={'name': task_name, 'idList': column['id'], **auth_params})
            break
        else:
            create_column(column_name)
            requests.post(base_url.format('cards'), data={'name': task_name, 'idList': column['id'], **auth_params})
            break


#Функция удаления задачи
def delete_task(task_id, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    for column in column_data:
        if column['name'] == column_name:
            task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
            for task in task_data:
                if task['id'] == task_id:
                    # Удалим задачу с именем _name_
                    requests.delete(base_url.format('cards') + '/' + task['id'], params=auth_params)
                    break


def create_column(column_name):
    requests.post(base_url.format('boards') + "/" + board_id + '/lists', params={'name': column_name, **auth_params})


def move(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Среди всех колонок нужно найти задачу по имени и получить её id
    task_id = None
    for column in column_data:
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name:
                task_id = task['id']
                break
        if task_id:
            break

            # Теперь, когда у нас есть id задачи, которую мы хотим переместить
    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу
    for column in column_data:
        if column['name'] == column_name:
            # И выполним запрос к API для перемещения задачи в нужную колонку
            requests.put(base_url.format('cards') + '/' + task_id + '/idList', data={'value': column['id'], **auth_params})
            break

def check_replays(task_name):
    # Создаем массив, куда сохраняем строку, если она есть в какой-либо колонке
    tasks_list = []
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    # Среди всех колонок нужно найти задачу по имени и получить её id
    task_id = None
    for column in column_data:
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == task_name:
                task_dict = {
                    'task_name': task['name'],
                    'ID': task['id'],
                    'column_name': column['name']
                }
                tasks_list.append(task_dict)
    if len(tasks_list) > 1:
        print('В колонках встречаются задачи с одинаковым названием')
        for i in range(len(tasks_list)):
            print('\t' + str(i) + ' - ' + 'Имя задачи: ' + tasks_list[i]['task_name']
                  + ', ID задачи: ' + tasks_list[i]['ID']
                  + ', Находится в колонке: ' + tasks_list[i]['column_name'] )
        print('Что вы хотите сделать?')
        print('1 - удалить')
        print('2 - оставить все так')
        a = int(input('Введите число: '))
        if a == 1:
            answer = int(input('Введите номер(первое число) задачи, которую хотите удалить: '))
            if answer > -1 and answer < len(tasks_list):
                current_task = tasks_list[answer]
                delete_task(current_task['ID'], current_task['column_name'])
                print('Задача удалена')
            else:
                print('Число вне диапозона')
        elif a == 2:
            print('Завершение работы')
        else:
            print('Число вне диапозона')

    else:
        print('Одинаковых задач нет!!!')




if __name__ == "__main__":
    if len(sys.argv) < 2:
        read()
    elif sys.argv[1] == 'create_task':
        create_task(sys.argv[2], sys.argv[3])
        check_replays(sys.argv[2])
    elif sys.argv[1] == 'delete_task':
        delete_task(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'create_column':
        create_column(sys.argv[2])
    elif sys.argv[1] == 'check_replays':
        check_replays(sys.argv[2])
