shopping = pd.Series(['молоко', 'хамон', 'хлеб', 'картошка', 'огурцы'])
print(shopping)  # список того, что нужно купить  
print()
print(
    shopping.where(shopping != 'хамон', 'обойдусь')
)  # тот же список после проверки баланса карты

# some new code

#new branch here

#github

IT_names = pd.DataFrame(
    {
        'name': ['Саша', 'Саша', 'Саша', 'Игорь', 'Игорь', 'Максим', 'Максим'],
        'surname': [
            'Иванов',
            'Попов',
            'Сидоров',
            'Смирнов',
            'Крылов',
            'Курепов',
            'Максимов',
        ],
    }
)
print(IT_names)
print
# метод groupby(), автоматически перебирающий уникальные значения. Если передать ему столбец, то он вернёт 
# последовательность пар: значение столбца — срез данных с этим значением. 
for developer_name, developer_data in IT_names.groupby('name'):
    print(
        'Имя {} встречается {} раза'.format(
            developer_name, len(developer_data)
        )
    )
# то же другим способом	
print(IT_names.groupby('name').count())

import pandas as pd

data = pd.read_csv('/datasets/visits.csv', sep='\t')

# фильтруем слишком быстрые и медленные заезды и АЗС
data['too_fast'] = data['time_spent'] < 60
data['too_slow'] = data['time_spent'] > 1000
too_fast_stat = data.pivot_table(index='id', values='too_fast')
good_ids = too_fast_stat.query('too_fast < 0.5')
good_data = data.query('id in @good_ids.index')
good_data = good_data.query('60 <= time_spent <= 1000')

# считаем данные по отдельным АЗС и по сетям
station_stat = data.pivot_table(index='id', values='time_spent', aggfunc='median')
good_stations_stat = good_data.pivot_table(index='id', values='time_spent', aggfunc='median')
stat = data.pivot_table(index='name', values='time_spent')
good_stat = good_data.pivot_table(index='name', values='time_spent', aggfunc='median')
stat['good_time_spent'] = good_stat['time_spent']

id_name = good_data.pivot_table(index='id', values='name', aggfunc=['first', 'count'])
id_name.columns = ['name', 'count']
station_stat_full = id_name.join(good_stations_stat)

# считаем показатели сетей из показателей АЗС,
# а не усреднённые заезды на все АЗС сети
good_stat2 = (
    station_stat_full
    .query('count > 30')
    .pivot_table(index='name', values='time_spent', aggfunc=['median', 'count'])
)
good_stat2.columns = ['median_time', 'stations']
final_stat = stat.join(good_stat2)

#выявили аномалии, отфильтровали данные, создали показатели для типичного времени заезда и изучили влияние большого числа аномальных заездов на эти показатели. Проверьте всё ещё разок, прежде чем делиться результатами. Для начала визуализируйте распределение лучших показателей заездов с типичной продолжительностью по сетям АЗС.

#median_time— это медиана для распределения медианной продолжительности заправки по АЗС в каждой сети
(final_stat
    .sort_values(by='median_time', ascending=True)
    .plot(kind='bar', y='median_time', figsize=(10, 5)) 
)

#Таблица final_stat была создана объединением таблиц stat (включает все АЗС) и good_stat2 (исключает АЗС с малым числом заездов). Так как в join() по умолчанию левое соединение, индексы из final_stat будут идентичны индексам из stat. Поэтому любой индекс из таблицы stat, которого нет в таблице good_stat2, после объединения получит значение NaN. Наведите порядок в графике, удалив значения NaN.

(final_stat
     .dropna(subset=['median_time'])
     .sort_values(by='median_time', ascending=True)
     .plot(kind='bar', y='median_time', grid=True, figsize=(10, 5))
)

#как число заправочных станций распределяется по сетям.- -  гистограмму, отображающую число АЗС внутри сетей. 
final_stat['stations'].hist(bins=100)

big_nets_stat = final_stat.query('stations > 10')

#Лучшие показатели средней продолжительности заправки содержатся в таблице good_stat2 и рассчитываются по данным station_stat_full
#Повторите вычисления, но вместо того, чтобы группировать данные по столбцу name, сгруппируйте данные по новому столбцу, содержащему категорию Другие. Чтобы создать этот столбец в таблице station_stat_full, примените метод where() для сравнения столбца name в station_stat_full с индексами big_nets_stat

station_stat_full['group_name'] = (
    station_stat_full['name']
    .where(station_stat_full['name'].isin(big_nets_stat.index), 'Другие')
)

stat_grouped = (
    station_stat_full
    .query('count > 30')
    .pivot_table(index='group_name', values='time_spent', aggfunc=['median', 'count'])
)
stat_grouped.columns = ['time_spent', 'count']
stat_grouped = stat_grouped.sort_values(by='time_spent', ascending=True)

stat_grouped.plot(kind='pie', y='count', figsize=(8, 8))
# Например, если в одной сети больше АЗС с продолжительностью заездов по 60–70 секунд, чем в других, это может понижать медианное значение. Чтобы проверить, не происходит ли такое, сгруппируйте данные из good_data по group_name и постройте гистограммы. Первым делом создайте столбец для группировки.
good_data['group_name'] = (
    good_data['name']
    .where(good_data['name'].isin(big_nets_stat.index), 'Другие')
)

for name, group_data in good_data.groupby('group_name'):
    group_data['time_spent'].hist(bins=50) #интересно, но неверно
	group_data.plot(kind='hist', y='time_spent', bins=50, label=name)
	group_data.plot(kind='hist', y='time_spent', bins=50, title=name)