"""
tushare_easy utils

"""
from __future__ import print_function
import os
from warnings import warn
import arrow
import pandas as pd
import tushare as ts
from unipath import Path
from . import consts as CONSTS


def get_data(code, ktype='d', start=None, end=None):
    if start is None:
        start = ''
    if end is None:
        end = ''

    print(code, ktype)
    return ts.get_k_data(code, ktype=ktype,
                         start=start, end=end,
                         retry_count=CONSTS.retry_count,
                         pause=CONSTS.pause)


def set_date_index(df, labels=CONSTS.index_labels_date):
    """
    set date as df's index

    Parameters
    ----------
    df : pandas.DataFrame
        data
    labels : list-like
        labels using to set as df index, sequenced preferred

    Returns
    -------
    pandas.DataFrame
        data with index set by a label in labels

    """
    for label in labels:
        if label in df.columns:
            df = df.set_index(label)
            df.index = pd.DatetimeIndex(df.index)
            return df
        else:
            raise Exception('COLUMNS NAME NOT FOUNDED IN %r' % labels)


def prep(df,):
    df.pop('code')
    df = df.drop(df.index[-1])
    return set_date_index(df)


def get_demo(df):
    return df.head(1).append(df.tail(1))


def get_demo_new(df_last, df_newer):
    return df_last.head(1).append(df_newer.tail(1))


def read_data(filepath, header=0):
    """
    read data from file

    always with index, with header default

    Parameters
    ----------
    filepath : str

    Returns
    -------
    pd.DataFrame
    """
    return pd.read_table(filepath, parse_dates=True,
                         index_col=0, header=header)


def save(df, filepath, mode='w', header=False):
    df.to_csv(filepath, header=header, sep='\t', mode=mode)


def fmt_filename(name_list):
    """
    format filename

    Parameters
    ----------
    name_list : list like [code, start, end, ktype]

    Returns
    -------
    str
        filename
    """
    return CONSTS.filename_sep.join(name_list)


def fmt_filename_demo(name_list):
    name_list.append(CONSTS.demo)
    return CONSTS.filename_sep.join(name_list)


def split_filename(filename):
    return filename.split(CONSTS.filename_sep)


def extract_start_end(df):
    """
    format start and end time

    Parameters
    ----------
    df : pd.DataFrame
        data with setting time as index

        time format:
            '%Y-%m-%d %H:%M' or
            '%Y-%m-%d'

    Returns
    -------
    (start, end) : tuple
        tuple with two datetime string elements
    """
    fmt_time = '%Y-%m-%d-%H-%M'
    start = df.index[0].strftime(fmt_time)
    end = df.index[-1].strftime(fmt_time)
    return start, end


def get_local(code, ktype='d', path='.'):
    """
    get last file and demo

    Parameters
    ----------
    code : str
    ktype : str
    path : str
        where to search file

    Returns
    -------
    filename_demo : filename of demo

    """
    path = Path(path)
    pattern = CONSTS.filename_sep.join([ktype, CONSTS.demo])
    pattern = '%s%s*%s%s' % (code, CONSTS.filename_sep, CONSTS.filename_sep,
                             pattern)
    file_list = path.listdir(pattern, names_only=True)
    if len(file_list) == 1:
        return file_list[0]
    elif len(file_list) == 0:
        return warn('NO ITEM')
    else:
        raise Exception('MORE THAN 1 ITEM')


def get_arrow(strftime):
    """
    get ``arrow.arrow.Arrow`` from str with local timezone info

    Parameters
    ----------
    strftime : str, with format '%Y-%m-%d-%M-%s'

    Returns
    -------
    ``arrow.arrow.Arrow``

    """
    time_tz = strftime + CONSTS.tz_local
    return arrow.get(time_tz, CONSTS.time_fmt)


def get_end_date(ktype='d'):
    """
    get up-to-date time of market

    Parameters
    ----------
    ktype : str, {'5', '15', '30', '60', 'd', 'w', 'm'}

    Returns
    -------
    end_datetime : ``arrow.arrow.Arrow``

    """
    today = arrow.utcnow()
    today = today.to(CONSTS.tz_local)
    start = today.shift(**CONSTS.datetime_shift_search[ktype])
    date_fmt = 'YYYY-MM-DD'
    start = start.format(date_fmt)
    end = today.format(date_fmt)
    df = ts.get_k_data(CONSTS.code_std, index=True,
                       ktype=ktype, start=start, end=end)
    if df.empty:
        raise Exception('NO DATA FOUNDED')
    df = prep(df)
    if df.empty:
        return df
    _, end_std = extract_start_end(df)
    return get_arrow(end_std)


def get_threshhold_datetime(time_str, ktype='d'):
    """
    get threshhold of recent time locally

    Parameters
    ----------
    time_str : str, with format '%Y-%m-%d-%M-%s'
    ktype : str, {'5', '15', '30', '60', 'd', 'w', 'm'}

    Returns
    -------
    threshhold_datetime : ``arrow.arrow.Arrow``

    """
    time_arrow = get_arrow(time_str)
    time_arrow = time_arrow.shift(**CONSTS.datetime_shift[ktype])

    if ktype == '60':
        return time_arrow.ceil('hour')
    elif ktype == 'd':
        return time_arrow.ceil('day')
    elif ktype == 'w':
        return time_arrow.ceil('week')
    elif ktype == 'm':
        return time_arrow.ceil('month')
    elif ktype in ['5', '15', '30']:
        return time_arrow.ceil('minute')
    else:
        raise Exception('KTYPE ERROR')


def is_up_to_date(end_local_str, ktype='d',):
    """
    check whether local data is up-to-date

    Parameters
    ----------
    end_local_str : str, with format '%Y-%m-%d-%M-%s'
    ktype : str, {'5', '15', '30', '60', 'd', 'w', 'm'}

    Returns
    -------
    boolean

    """
    # saved last date
    end_local = get_threshhold_datetime(end_local_str, ktype)
    end_std = get_end_date(ktype)
    if end_std > end_local:
        return False
    else:
        return True


def down2save(code, ktype='d', start=None, end=None, path='.'):

    cwd = Path(path)
    cwd.chdir()
    df = get_data(code, ktype, start, end)
    if df.empty:
        return df

    df = prep(df)
    if df.empty:
        return df

    df_demo = get_demo(df)
    print(df_demo)

    start, end = extract_start_end(df_demo)

    name_list = [code, start, end, ktype]
    filename = fmt_filename(name_list)
    filename_demo = fmt_filename_demo(name_list)
    save(df, filename)
    save(df_demo, filename_demo, header=True)


def down2save_update(code, ktype='d', start=None, end=None, path='.'):
    """
    get k_chart date and save them locally, and update them

    get k_chart data using `tushare.get_k_data`
    save data locally with tab separated files
    could append data line by line if getting newer

    Parameters
    ----------
    code : str
    ktype : str, {'5', '15', '30', '60', 'd', 'w', 'm'}
    path : str
        where to search files locally

    Returns
    -------

    """
    cwd = Path(path)
    cwd.chdir()

    filename_demo_local = get_local(code, ktype, path)
    if not isinstance(filename_demo_local, str):
        return down2save(code, ktype, start, end, path)

    df_demo_local = read_data(filename_demo_local)
    print(df_demo_local)
    start_local, end_local = extract_start_end(df_demo_local)
    if is_up_to_date(end_local, ktype):
        print('data up to date')
        return

    name_list_demo_local = split_filename(filename_demo_local)
    filename_local = fmt_filename(name_list_demo_local[:-1])

    df = get_data(code, ktype, start, end)
    if df.empty:
        return df
    df = prep(df)
    if df.empty:
        return df
    df_newer = df.loc[df.index > df_demo_local.index[-1]]
    if df_newer.empty:
        return df_newer

    df_demo_new = get_demo_new(df_demo_local, df_newer)
    print(df_demo_new)
    _, end_newer = extract_start_end(df_demo_new)

    filename_new = [code, start_local, end_newer, ktype]
    filename_new = fmt_filename(filename_new)

    save(df_newer, filename_local, mode='a')
    os.rename(filename_local, filename_new)
    print('rename %s %s' % (filename_local, filename_new))

    filename_demo_new = fmt_filename_demo(filename_new)
    save(df_demo_new, filename_demo_new, header=True)

    os.remove(filename_demo_local)
    print('remove %s' % filename_demo_local)
