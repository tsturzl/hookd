#WIP

This is currently uncomplete and a work in progress. Do not use, currently untested.

##What is it?

Hookd is a simple solution to consuming webhooks without needing to worry about the hassle of creating a webserver. Hookd allows you to consume a webhook and pass that data to any script regardless of language. This makes setting up a github push webhook for auto-deploy stupid simple. In return it also lets you output JSON to be sent back in a response. All using standard i/o.

###Asynchronous by design

Built upon twisted matrix and the klien micro-framework, hookd is build completely asynchronous from front to back to scale to high demands.

###Configuration

The config file is YAML format, and its dead simple.

Examples:

``` yaml
---
githubPush:
  cmd: /home/appUser/deploy.sh
  env:
    DEPLOY_ENV: production
    BRANCH: master
```

route: `/hook/githubpush[POST]`


__Options:__

 * cmd
   * Absolute path of command to run
 * env
   * Optionally pass environment variables as key value pairs

###Inspiration

[websocketd](http://websocketd.com/) CGI for websockets
[Git-Auto-Deploy](https://github.com/olipo186/Git-Auto-Deploy) Webhook consuming service for git push events from popular source code hosts.

###Contributions

Anything helps. Got an idea? Put it in a ticket. Pull requests are welcomed.

Some short term goals is to map json values with dot notation(eg. `commit[0].user.id`) to arguments for the command line. Another useful feature would be to provie a feature to keep the script alive and write to stdin upon hook events.

###License

Published under a MIT License.
