# -*- coding: utf-8 -*-
import datetime
import json
import os

import requests

# Slack hooks
SLACK_HOOKS_URL = "https://hooks.slack.com/services/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"
TOGGL_API_TOKEN = "7cad27f9b07abbdd83767e87dc77d5ea"
file_name = "./history.txt"


def get_toggl():
    headers = {"content-type": "application/json"}
    auth = requests.auth.HTTPBasicAuth(TOGGL_API_TOKEN, "api_token")
    current = requests.get("https://track.toggl.com/api/v8/time_entries/current", auth=auth, headers=headers)
    if current.status_code != 200:
        print("togglの情報取得に失敗しました")
        return None, [], None

    current_json = current.json()
    if not current_json["data"]:
        return None, [], None
    print("##################################################")
    print(f'{current_json["data"]}')
    print("##################################################")
    description = current_json["data"]["description"]

    # この時点でプロジェクト名をとってきておく
    pname = None
    if "pid" in current_json["data"]:
        pid = current_json["data"]["pid"]
        pname = get_project_name(pid)
        print(f"pid: {pid}, pname: {pname}, description: {description}")

    return pname, current_json["data"]["tags"], description


def get_project_name(pid):
    headers = {"content-type": "application/json"}
    auth = requests.auth.HTTPBasicAuth(TOGGL_API_TOKEN, "api_token")
    current = requests.get(f"https://track.toggl.com/api/v8/projects/{pid}", auth=auth, headers=headers)

    if current.status_code != 200:
        print("togglの情報取得に失敗しました")
        return None

    current_json = current.json()
    if not current_json["data"]:
        return None
    return current_json["data"]["name"]


def check_old_toggl(now_task):
    prev_task = None
    with open(file_name, mode="r", encoding="utf-8") as f:
        history = f.read()
        prev_task = history.strip()

    write_history(now_task)
    return (prev_task == now_task), prev_task


def write_history(str_history):
    with open(file_name, mode="w", encoding="utf-8") as fw:
        fw.write(str_history)


def write_slack(title, description):
    text = f"""【{title}】 `{description}` """

    payload = {"username": "Toggl", "text": text, "icon_emoji": ":clock10:"}

    requests.post(SLACK_HOOKS_URL, data=json.dumps(payload))


if __name__ == "__main__":
    now = datetime.datetime.now()
    now_str = now.strftime("%Y/%m/%d %H:%M:%S")

    # 現在のタスクの取得
    pname, tags, description = get_toggl()
    now_task = f'{description} ({pname}：{", ".join(tags)})'
    is_same, prev_task = check_old_toggl(now_task)

    if not pname and not description:
        print(f"[{now_str}] not pname+description")
        stat = os.stat(file_name)
        mdt = datetime.datetime.fromtimestamp(os.stat(file_name).st_mtime)
        if now.day != mdt.day:
            # 日付が変わっていたら、問答無用で終了
            write_history("")
            # ログクリア
            os.remove("./out.log")
            exit(1)
        elif prev_task and not description and "None" not in prev_task:
            # slackへの書き込み(次が始まってない時だけ)
            print(f"[{now_str}] write end")
            write_slack("作業終了", prev_task)

            # 終了して次が始まってない場合
            write_history("")
            exit(1)

    if not pname:
        # プロジェクト名が入ってない場合、スルー
        exit(1)

    if is_same:
        print(f"[{now_str}] same")
        # 前回取得したものと同じ場合は終了
        exit(1)

    if description:
        print(f"[{now_str}] write start")
        # slackへの書き込み
        write_slack("作業開始", now_task)
