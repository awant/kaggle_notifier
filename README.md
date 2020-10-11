# kaggle_notifier

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
