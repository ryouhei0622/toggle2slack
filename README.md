# toggleからステータスを取得してslackに投稿

一旦終わり！！！

### issue1のアドホック的な解決策
```
sudo launchctl bootout gui/501 /Users/**/Library/LaunchAgents/toggle2slack.plist
sudo launchctl bootstrap gui/501 /Users/**/Library/LaunchAgents/toggle2slack.plist
```

次はGAS使ってステータスを変更するのをやる(2h想定)
