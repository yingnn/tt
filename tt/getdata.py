from __future__ import print_function
import os
from unipath import Path
import functools
from .utils import down2save_update
from . import consts as CONSTS


__all__ = ['RunFunc', 'GetData']


def _chcwd(path):
    def decorated(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            os.chdir(path)
            return f(*args, **kwargs)
        return wrapper
    return decorated


class Base(object):
    """
    set and make directory
    """

    def __init__(self, home='.'):
        """
        set home directory

        Parameters
        ----------
        home : str
            set a directory as home

        Returns
        -------
        """
        self._home = Path(home).absolute()

    def __str__(self):
        return self.home

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.home)

    # def __abs(self, string):
    #     return os.path.abspath(string)

    @property
    def home(self):
        return self._home.__str__()

    @home.setter
    def home(self, path):
        self._home = Path(path).absolute()

    def make_home(self, force=False):
        """
        make home directory

        Parameters
        ----------
        force : bool
            if True, if home exists and is a dir that
            containing contents, then delete contents
            in it, if exists and not a dir, remove it
            and make dir

        Returns
        -------

        """
        self.__mkdir(force)

    def __mkdir(self, force=False):
        if self._home.exists():
            if not self._home.isdir():
                if not force:
                    raise Exception('%s exists but is not a dir' % self.home)
                self._home.remove()
                self._home.mkdir()
            if force:
                self._home.rmtree()
                self._home.mkdir()
        else:
            self._home.mkdir(parents=True)

    def __rmdir(self, force=False):
        if self._home.exists():
            if not self._home.isdir():
                if not force:
                    raise Exception('%s exists but is not a dir' % self.home)
                self._home.remove()

            if force:
                self._home.rmtree()
            else:
                self._home.rmdir()

    def rm_home(self, force=False):
        """
        remove home directory

        Parameters
        ----------
        force : bool
            if True, if home exists and is a dir that
            containing contents, then delete it and
            it's contents, if exists and not a dir,
            remove then

        Returns
        -------

        """
        self.__rmdir(force)


class RunFunc(Base):
    """
    run function in target directory

    setup target directory and function,
    then run function within target
    directory
    """

    def __init__(self, home='.'):
        super(RunFunc, self).__init__(home)
        self._func = None

    def set_func(self, func):
        """
        set a function to run

        Parameters
        ----------
        func : function

        Returns
        -------
        """
        self._func = func

    @property
    def func(self):
        if hasattr(self, '_func'):
            return self._func

    def run(self, *args, **kwargs):
        """
        run func

        func parameter passed by args and kwargs

        Parameters
        ----------
        args : args of `self.func`
        kwargs : kwargs of `self.func`

        Returns
        -------

        """
        @_chcwd(self._home)
        def wrap(*args, **kwargs):
            return self._func(*args, **kwargs)

        return wrap(*args, **kwargs)


class GetData(RunFunc):
    """
    get data and save them locally

    get df using tushare's `get_k_date` function
    save df to local without duplication
    """

    def __init__(self, codes, ktypes=CONSTS.ktypes, start=None, end=None, home='.'):
        """
        Parameters
        ----------
        home : str, current work directory
        codes : list-like
        ktypes: list-like
        start : str, time format '%Y-%m-%d-%H-%M'
        end : str, same format to `start`

        Returns
        -------

        Examples
        --------
        >>> import pandas as pd
        >>> import tushare as ts
        >>> ktypes = ['5', '15', '30', '60', 'd', 'w', 'm']
        >>> home = os.path.join(os.environ['HOME'], 'data', 'ts', 'k_chart')
        >>> get_code = RunFunc(home)
        >>> get_code.set_func(ts.get_stock_basics)
        >>> codes = get_code.run().index.values
        >>> getdf = GetData(codes, ktypes, home=home)
        >>> getdf.run_loop()

        """
        super(GetData, self).__init__(home)
        self._codes = codes
        self._ktypes = ktypes
        self._start = start
        self._end = end
        self.set_func(down2save_update)

    @property
    def codes(self):
        return self._codes

    @property
    def ktypes(self):
        return self._ktypes

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    def run_loop(self,):
        home = self._home
        for code in self._codes:
            self._home = home.child(code)
            print(self.home)
            self.make_home()
            for ktype in self._ktypes:
                self.run(code, ktype, self._start, self._end, )
            self._home = home  # back to original path
