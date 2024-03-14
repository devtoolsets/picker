基于github action 实现的自动化推送系统

### 订阅源

推荐订阅源：

- [CustomRSS](config/CustomRSS.opml)

其他订阅源：

- [CyberSecurityRSS](https://github.com/zer0yu/CyberSecurityRSS)
- [Chinese-Security-RSS](https://github.com/zhengjim/Chinese-Security-RSS)
- [awesome-security-feed](https://github.com/mrtouch93/awesome-security-feed)
- [SecurityRSS](https://github.com/Han0nly/SecurityRSS)
- [安全技术公众号](https://github.com/ttttmr/wechat2rss)
- [SecWiki 安全聚合](https://www.sec-wiki.com/opml/index)
- [Hacking8 安全信息流](https://i.hacking8.com/)

非安全订阅源：

- [中文独立博客列表](https://github.com/timqian/chinese-independent-blogs)

**添加自定义订阅源**

1. 在 `config.yml` 中添加本地或远程仓库：

```yaml
rss:
  CustomRSS:
    enabled: true
    filename: CustomRSS.opml
  CyberSecurityRSS:
    enabled: true
    url: >-
      https://raw.githubusercontent.com/zer0yu/CyberSecurityRSS/master/CyberSecurityRSS.opml
    filename: CyberSecurityRSS.opml
  CyberSecurityRSS-tiny:
    enabled: false
    url: 'https://raw.githubusercontent.com/zer0yu/CyberSecurityRSS/master/tiny.opml'
    filename: CyberSecurityRSS-tiny.opml
  Chinese-Security-RSS:
    enabled: true
    url: >-
      https://raw.githubusercontent.com/zhengjim/Chinese-Security-RSS/master/Chinese-Security-RSS.opml
    filename: Chinese-Security-RSS.opml
  awesome-security-feed:
    enabled: true
    url: >-
      https://raw.githubusercontent.com/mrtouch93/awesome-security-feed/main/security_feeds.opml
    filename: awesome-security-feed.opml
  SecurityRSS:
    enabled: true
    url: 'https://github.com/Han0nly/SecurityRSS/blob/master/SecureRss.opml'
    filename: SecureRss.opml
  wechatRSS:
    enabled: true
    url: 'https://wechat2rss.xlab.app/opml/sec.opml'
    filename: wechatRSS.opml
  chinese-independent-blogs:
    enabled: false
    url: >-
      https://raw.githubusercontent.com/timqian/chinese-independent-blogs/master/feed.opml
    filename: chinese-independent-blogs.opml
```

2. 自定义rss源位于`config/CustomRSS.opml`中

    非rss源可以使用rsshub转发


### 本地搭建

```sh
pip3 install -r requirements.txt
./collect.py
```

### github部署

操作比较简单, clone本仓库, 然后创建一个空项目, 将该仓库push即可.

在secret中配置`PICKER_ACCESS_TOKEN`, 点击这里[生成](https://github.com/settings/tokens/new), 只需要给repo权限即可.

然后在github secret中配置`PICKER_ACCESS_TOKEN`

