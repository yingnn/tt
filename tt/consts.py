"""tushare_easy constants

"""

index_labels_str = ['code']
index_labels_date = ['date', 'month']

filename_sep = '_'

demo = 'demo'

retry_count = 3
pause = .1

tz_local = '+08:00'

code_std = '000001'

time_fmt = 'YYYY-MM-DD-HH-mmZZ'

datetime_shift_search = {
    '5': {'days': -10},
    '15': {'days': -10},
    '30': {'days': -10},
    '60': {'days': -10},
    'd': {'days': -10},
    'w': {'weeks': -2},
    'm': {'months': -2},
}

datetime_shift = {
    '5': {'minutes': 5},
    '15': {'minutes': 15},
    '30': {'minutes': 30},
    '60': {'hours': 1},
    'd': {'days': 1},
    'w': {'weeks': 1},
    'm': {'months': 1},
}
