archivy_pocket is an official Extension for [Archivy](https://github.com/archivy/archivy).

It allows users to sync their pocket bookmarks to the knowledge base.

![demo](https://github.com/archivy/archivy_pocket/blob/master/demo.gif)


## Install

You need to have `archivy` already installed.
Run `pip install archivy_pocket`.

## Usage

To do this, you need to create a Pocket API app [here](https://getpocket.com/developer/apps/). It only needs the `Retrieve` permissions and is of type `Web`.

Then, run:

```python
archivy pocket auth <your pocket key>
```

This will prompt a webpage asking you to allow the Pocket App to retrieve your bookmarks. Click accept.

Run `archivy pocket complete` to finish up the auth process.


Now that you're set up, all you need to do to is run `archivy pocket sync` to fetch your latest bookmarks.

You can also use the plugin through the web interface at `/plugins`.

