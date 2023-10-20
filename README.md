### 新增对`front_matter`的翻译功能，直接利用ChatGPT进行格式识别

------------------------------------------------------------------------------------------------------
# Auto-i18n：使用 ChatGPT 的自动多语言翻译工具

Auto-i18n 是一个使用 ChatGPT 自动将 Markdown 文件批量翻译为多语言的工具。

它实现了博客文章 i18n(Internationalization) 的完全自动化。你仅需将博文推送至 GitHub 仓库，即可借助 GitHub Actions 实现自动转译为多种语言。（目前支持英语、西班牙语和阿拉伯语，后续将提供更多语言支持）

附：[个人博客](https://wiki-power.com) 实现 i18n 后的效果：

![](https://img.wiki-power.com/d/wiki-media/img/202310151317234.png)

## 快速上手

1. 首先，将仓库克隆到本地。
2. 将 `env_template.py` 重命名为 `env.py`，并填写你的 ChatGPT API 信息。你可以在项目 [**chatanywhere/GPT_API_free**](https://github.com/chatanywhere/GPT_API_free) 申请免费的 API 密钥。
3. 运行 `pip install openai PyYAML` 安装必要的依赖。
4. 运行 `auto-translater` 程序，它会自动处理测试目录 `testdir/to-translate` 下的所有 Markdown 文件，批量翻译为英语、西班牙语、阿拉伯语。（后续将提供更多语言支持）

## 详细描述

程序 `auto-translater.py` 的运行逻辑如下：

1. 程序会自动处理测试目录 `testdir/to-translate` 下的所有 Markdown 文件，你可以在 `exclude_list` 变量中排除不需要翻译的文件。
2. 处理后的文件名会被记录在自动生成的 `processed_list.txt` 中。下次运行程序时，已处理的文件将不会再次翻译。
3. 对于原本使用英文撰写的文章，程序不会重新翻译成英文，也不会翻译回中文，而会翻译为其他语言。你需要在文章中添加字段 `> This post was originally written in English.`（注意在上下各留一个空行），以便程序识别。请参考 [测试文章\_en.md](testdir/to-translate/测试文章_en.md)。
4. 如果需要重新翻译特定文章（例如，翻译结果不准确，或文章内容发生更改等），你可以在文章中加入字段 `[translate]`（同样需要在上下各留一个空行）。这将会忽略 `exclude_list` 和 `processed_list` 的规则，强制进行翻译处理。请参考 [测试文章\_force-mark.md](testdir/to-translate/测试文章_force-mark.md)。

## GitHub Actions 自动化指南

你可以在自己项目仓库下创建 `.github/workflows/ci.yml`，当检测到 GitHub 仓库更新后，可以使用 GitHub Actions 自动进行翻译处理，并自动 commit 回原仓库。

`ci.yml` 的内容可参考模板：[ci_template.yml](ci_template.yml)

你需要在仓库的 `Settings` - `Secrets and variables` - `Repository secrets` 中添加两个 secrets：`CHATGPT_API_BASE` 和 `CHATGPT_API_KEY`，并在程序 `auto-translater.py` 中将 `import env` 语句注释掉。

## 错误排除

1. 如果需要验证 ChatGPT API key 的可用性，可以使用程序 [verify-api-key.py](Archive/verify-api-key.py) 进行测试。如果在国内使用官方API，需要有本地代理。
2. 如果 Markdown 中的 Front Matter 无法被正常识别，可以使用程序 [detect_front_matter.py](Archive/detect_front_matter.py) 测试。
3. 使用 GitHub Actions 遇到问题时，请优先检查路径引用是否正确（例如 `dir_to_translate` `dir_translated_en` `dir_translated_es` `dir_translated_ar` `processed_list`）。

## 待解决的问题

1. 如果 Markdown 中包含 Front Matter，将保留 Front Matter 的原始内容。Front Matter 部分参数翻译的功能正在开发中。 
2. 如果你提供的文章不完整，有可能会出现 ChatGPT 帮你翻译并自动续写完整的情况（迷）。
3. 在某些特殊的情况下，可能会出现翻译不准确、或某些字段没有翻译的情况，建议翻译后手动校验再发布文章。

## 贡献

欢迎你参与本项目的改进！如果您想要贡献代码、报告问题或提出建议，请查看 [贡献指南](CONTRIBUTING.md)。

## 版权和许可

本项目采用 [MIT 许可证](LICENSE)。

## 问题和支持

如果你在使用 Auto-i18n 时遇到任何问题，或者需要技术支持，请随时 [提交问题](https://github.com/linyuxuanlin/Auto-i18n/issues)。

## 致谢

感谢 [**chatanywhere/GPT_API_free**](https://github.com/chatanywhere/GPT_API_free) 提供的免费 ChatGPT API key。

[![Star History Chart](https://api.star-history.com/svg?repos=linyuxuanlin/Auto-i18n&type=Date)](https://star-history.com/#linyuxuanlin/Auto-i18n&Date)
