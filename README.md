This is the README for **TheGoddamnChatbot**. 

*What is this?, you ask. It's the Goddamn Chatbot, that's what!*

# Getting this code to work #
For starters, you're going to need to meet a few dependencies:

 * A modern *nix system (should work on OSX, in theory)
 * Python 2.6+ (2.5 can work, if you backport some libs)
 * The following packages installed, on your `PYTHONPATH`:
   * [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)
   * [psutil](http://code.google.com/p/psutil/)
   * [dnspython](http://www.dnspython.org/)
   * [pyxmpp](http://pyxmpp.jajcus.net/)
   * [subprocess](http://code.google.com/p/python-subprocess32/) (comes with 2.6+ by default)
   * [twython](http://github.com/ryanmcgrath/twython)

The `dependencies.py` script can tell you which modules you're missing.
It also patches some old-style classes in the pyxmpp module.
Once it reports that everything is in order, you should be able to run
`cb_repl.py` and experiment with the triggers.

To actually run chatbot in a MUC room, edit the constants in 
  `config.py` to point to your room and server.

# Playing with this code #
 * The easiest (but least fun) thing to play with is `cb_repl.py`.
   * It provides a REPL-like environment for running chatbot's trigger commands.
   * Note that not all of them will work outside of the chatroom context.
 * Load up chatbot by running `bot.py`
 * Load an auto-responding Shakespeare bot with `shakespeare.py`
 * Load a clone of someone in your Pidgin logs with `clone.py`
 * Interact with a MUC room in your terminal with `cli.py`

