.. _quickstart:

Quickstart
==========

.. module:: terminal

Eager to get started? This page gives a good introduction in how to get started
with Terminal. This assumes you already have Terminal installed. If you do not,
head over to the :ref:`Installation <install>` section.

First, make sure that:

* Terminal is :ref:`installed <install>`


Let's get started with some simple examples.


Play with colors
----------------

Terminal would be better if it is colorful.

Begin by importing the Terminal module::

    >>> import terminal

Now, let's play with the colors::

    >>> print(terminal.red('red color'))
    >>> print(terminal.green_bg('green background'))

Available colors::

    black, red, green, yellow, blue, magenta, cyan, white

Available styles::

    bold, faint, italic, underline, blink, overline, inverse
    conceal, strike

But don't count on these styles, your terminal may be not able to show all of
them.


Verbose logging
---------------

Terminal programs need a simple and beatiful logging system. If it has a
verbose feature, it could helps a lot::

    >>> from terminal import log

Now, let's play with the verbose log::

    >>> log.info('play with the log')
    >>> log.verbose.info('a verbose log')
    >>> log.config(verbose=True)
    >>> log.verbose.info('a verbose log')

We can also control the logging level::

    >>> log.config(quiet=True)
    >>> log.info('info log will not show')
    >>> log.warn('but warn and error messages will show')


Prompt communication
--------------------

Many terminal programs will communicate with the users, this could be easy
with :class:`prompt`.

Let's create a prompt to ask the user's name::

    import terminal

    username = terminal.prompt('what is your name')

We could set a default name for the user::

    username = terminal.prompt('what is your name', 'Kate')

It is not a good idea to get a password with :class:`prompt`, instead,
terminal provided a :class:`password` for you::

    password = terminal.password('what is your password')

Want more on prompt?

We have :class:`terminal.confirm` and :class:`terminal.choose`.


Command line
------------

This is a replacement of **argparse** (or optparse).

Create a simple command parser with :class:`Command`::

    program = Command('foo', 'a description')

Add some options::

    program.option('-f, --force', 'force to process')
    program.option('-o, --output <output>', 'the output directory')

Let's make it work::

    program.parse()

    if program.output:
       print program.output

Save the code in a file (for example: foo.py), play in the terminal::

    Username@Machine: ~$ python foo.py -h
    Username@Machine: ~$ python foo.py -o src
    Username@Machine: ~$ python foo.py --output=src
    Username@Machine: ~$ python foo.py --output src

However, when creating a terminal tool, a subcommand is usually needed, we can
add subcommands via :class:`Command.action`::

    program = Command('foo', 'a description')
    program.option('-v, --verbose', 'show more logs')

    subcommand = Command('build', 'build the site')
    subcommand.option('-o, --output <output>', 'the output directory')

    program.action(subcommand)

    program.parse()

    if program.verbose:
        terminal.log.config(verbose=True)

Let's play with the more complex one::

    Username@Machine: ~$ python foo.py -h
    Username@Machine: ~$ python foo.py build -h
