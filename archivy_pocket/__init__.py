#!/usr/bin/env python3
import click
from archivy.extensions import get_db
from archivy import app
from tinydb import Query, operations
from datetime import datetime
from archivy.data import get_items, create_dir
from archivy.models import DataObj
import requests
import webbrowser

@click.group()
def pocket():
    pass

@pocket.command()
@click.argument("api_key")
def auth(api_key):
    with app.app_context():
        db = get_db()
        pocket = Query()
        request_data = {
            "consumer_key": api_key,
            "redirect_uri": "https://getpocket.com"
        }
        resp = requests.post(
            "https://getpocket.com/v3/oauth/request",
            json=request_data,
            headers={
                "X-Accept": "application/json",
                "Content-Type": "application/json"})
        new_data = {
            "type": "pocket_key",
            "consumer_key": api_key,
            "code": resp.json()["code"]}
        if db.search(pocket.type == "pocket_key"):
            db.update(new_data, pocket.type == "pocket_key")
        else:
            db.insert(new_data)
        click.echo("Allow archivy_pocket to retrieve data to your pocket account.")
        webbrowser.open(f"https://getpocket.com/auth/authorize?"
            f"request_token={resp.json()['code']}"
            f"&redirect_uri=https://getpocket.com"
            )


@pocket.command()
def complete():
    with app.app_context():
        db = get_db()
        try:
            pocket = db.search(Query().type == "pocket_key")[0]
        except:
            click.echo("Key not found")
            return
        auth_data = {
            "consumer_key": pocket["consumer_key"],
            "code": pocket["code"]}
        resp = requests.post(
            "https://getpocket.com/v3/oauth/authorize",
            json=auth_data,
            headers={
                "X-Accept": "application/json",
                "Content-Type": "application/json"})
        db.update(
            operations.set(
                "access_token",
                resp.json()["access_token"]),
            Query().type == "pocket_key")
        click.echo("Successfully completed auth process, you can now run archivy pocket sync to load the data")


@pocket.command()
def sync():
    with app.app_context():
        db = get_db()

        # update pocket dictionary
        pocket = db.search(Query().type == "pocket_key")[0]

        pocket_data = {
            "consumer_key": pocket["consumer_key"],
            "access_token": pocket["access_token"],
            "sort": "newest"}

        # get date of latest call to pocket api
        since = datetime(1970, 1, 1)
        create_dir("pocket")
        for post in get_items(
                path="pocket/",
                structured=False):
            date = datetime.strptime(post["date"].replace("-", "/"), "%x")
            since = max(date, since)

        since = datetime.timestamp(since)
        if since:
            pocket_data["since"] = since
        bookmarks = requests.post(
            "https://getpocket.com/v3/get",
            json=pocket_data).json()


        # api spec: https://getpocket.com/developer/docs/v3/retrieve
        # for some reason, if the `list` attribute is empty it returns a list instead of a dict.
        if not len(bookmarks["list"]):
            click.echo("No new bookmarks.")
        else:
            for pocket_bookmark in bookmarks["list"].values():
                if int(pocket_bookmark["status"]) != 2:
                    desc = pocket_bookmark["excerpt"] if int(
                        pocket_bookmark["is_article"]) else None
                    bookmark = DataObj(
                        desc=desc,
                        url=pocket_bookmark["resolved_url"],
                        date=datetime.now(),
                        type="pocket_bookmarks",
                        path="pocket")
                    bookmark.process_bookmark_url()
                    click.echo(f"Saving {bookmark.title}...")
                    bookmark.insert()
            click.echo("Done!")
