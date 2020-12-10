# Linksaver

Linksaver is a webapp that allows users to save links, take notes, and search, filter, and tag items.

I created this app becuase I was curious about a few new technologies. On the backend, I wanted to try out [Tom Christie](https://github.com/tomchristie)'s [Starlette](https://github.com/encode/starlette), which is awesome. On the frontend, I was curious about [Turbolinks](https://github.com/turbolinks/turbolinks) and [Stimulus](https://github.com/stimulusjs/stimulus). These libraries were used to build [Hey](https://hey.com)'s email app, which notably [doesn't use a client-rendered JavaScript framework](https://twitter.com/sstephenson/status/1272608117604397063) such as React. I have some observations about these technologies which I've told myself I'll write a blog post about someday. In the meantime, here's how to setup the project.

## Local development

```
docker-compose up
```

That's it. Go to a web browser and open `localhost:8000`.

## Deployment to Lightsail

Linksaver has three components that need to be setup: a Mongo database, the application container, and web extension.

### MongoDB

1. Go to [Lightsail](https://lightsail.aws.amazon.com/ls/webapp/home) and create an instance with Ubuntu 20.04. Copy the contents of [mongo-cloud-init](mongo-cloud-init.sh) into the launch script field. This script installs and configures MongoDB.
2. After the instance is ready, SSH into it and make sure that `mongo` was installed and is up by running `systemctl status mongod`.
3. Note the *internal ip* of your instance.

### Build and upload your container image

1. Go to [Lightsail](https://lightsail.aws.amazon.com/ls/webapp/home) and create a container service. Skip setting up your first deployment.
2. While your service is spinning up, build your container locally by running:

```
docker build . -t linksaver
```

3. Upload your image to Lightsail:

```
aws lightsail push-container-image --service-name <the name you gave> --label linksaver --image linksaver
```

4. Back on the Lightsail console, create a deployment with the following values.
    - Set an environment variable whose key is `DB_CONNECTION` and whose value is `mongodb://admin:admin@<private ip of your mongo instance>:27017/?authSource=admin`.
    - Open port `8000` with a protocol of `HTTP`.
5. After your deployment is complete, go to your service's public URL and create an account for yourself.

## Web extension

1. Open your Chromium based browser and go to the extensions page. E.g., `brave://extensions`. You may have to enable developer mode if you haven't already.
2. Click "Load unpacked" and choose the `webext` directory of this repository.
3. Click the new link icon and login. You can now start saving links. 🙂
