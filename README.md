# kaggle_notifier

@KaggleNotificationsBot (Telegram bot)

### What it is

A bot to recieve notifications about new competitions from kaggle (+ you can check the current state of a competition)

```
I'm helping you to receive new kaggle competitions to begin compete as soon as possible
Commands:
/subscribe - Subscribe to get new kaggle competitions daily
/unsubscribe - Unsubscribe from daily updates
/state <competition> - Get a current state of the competition
/help - Print this message again
```

A 'state' command example:

```
/state overfitting

title: Don't Overfit!
reward: $500
teams count: 259
days before deadline: -3439
evaluation metric: Area Under Receiver Operating Characteristic Curve
url: https://www.kaggle.com/c/overfitting

Leaderboard
place  score  date
    1  0.97119  2011-05-14
   10  0.96421  2011-05-14
   50  0.92627  2011-04-29
```

### How to deploy and run
(with dev configs: src/configs_dev)

1. Set up the right params in `src/configs_dev/` files

2. Change the last line of Dockerfile to:
`CMD [ "sh", "./run_dev.sh" ]`

3. Build a docker image and run:

```
docker build -t kaggle_notifier_img .
docker run -d -p 80:80 kaggle_notifier_img
```

4. To stop docker run: `docker stop <id>`
