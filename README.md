#kitinfo IRC bot
================

Core structure
--------------
The IRC bot is structured into several components:

- the core bot which maintains all other components
- a modules system for bot activities
- a providers system for additional services the bot must provide to the
  modules

A configuration file `config.ini` is used to define the bot's behaviour,
e.g. which servers and channels to join. For each server a individual
instance of the bot is being created, which can have individual modules
loaded.
Before first use of the bot, the example `config.ini.dist` must be copied
to `config.ini` and modified according to ones needs.

Modules system
--------------
Modules are used to define the bot's activities like responding to users,
listening for commands etc.
To define when to act how, hooks are being used.

The bot provides several different type of hooks:

- Command hooks: Methods attached to this hook will be called whenever
  a user mentions the specified command prefixed with a command identifier,
  usually a single special character like `.`, `@` etc.
- Action hooks: Methods attached to this hook will be called whenever
  the specified action is happening in a channel. Actions are all types
  of IRC events like `privmsg` or `userJoined`.
- Regular expression hooks: Methods attached to these hooks will be called
  whenever a `privmsg` matches the regular expression.
- Timeout hooks: These hooks can be used to call a function after a
  specified amount of time.

If the module requires additional service beyond the main features of the
bot, it must define those services in a list called `requires`.


Provider system
---------------
The bot uses so called "providers" to provide additional services,
that the bot does not include itself. These providers have to be placed
into the folder `providers` as a python module.

Whenever a service is required by a module (per `requires`), the bot
will load the additional service and provide it to the modules via an
attribute `provides` in the bot class. Modules can then access their
service through `bot.provides[providername]`.


Available Modules
-----------------

Currently, the following modules are available.

### Quiz

Quiz is a module to post a quiz question. It can load questions from
`jsonline`-files (each line one JSON document) with a questions in this
format:

```json
{
    "question": "What is this bot's name?",
    "answer": "broti",
    "options": ["kuchi", "broti", "wursti", "apfeli"]
}
```

`question` and `answer` are required, `options` is optional.


License
-------
This program is licensed under the Simplified BSD License.
