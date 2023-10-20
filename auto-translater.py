# -*- coding: utf-8 -*-
import os
import openai # pip install openai
import sys
import re
import yaml # pip install PyYAML
import env

# 设置 OpenAI API Key 和 API Base 参数，通过 env.py 传入
openai.api_key = os.environ.get("CHATGPT_API_KEY")
openai.api_base = os.environ.get("CHATGPT_API_BASE")

# 设置翻译的路径
dir_to_translate = "testdir/to-translate"
dir_translated = {
    "en": "testdir/docs/en",
    "es": "testdir/docs/es",
    "ar": "testdir/docs/ar"
}

exclude_list = ["index.md", "Contact-and-Subscribe.md", "WeChat.md"]  # 不进行翻译的文件列表
processed_list = "processed_list.txt"  # 已处理的 Markdown 文件名的列表，会自动生成

# 设置最大输入字段，超出会拆分输入，防止超出输入字数限制
max_length = 1800

# 由 ChatGPT 翻译的提示
tips_translated_by_chatgpt = {
    "en": "\n\n> This post is translated using ChatGPT, please [**feedback**](https://github.com/linyuxuanlin/Wiki_MkDocs/issues/new) if any omissions.",
    "es": "\n\n> Este post está traducido usando ChatGPT, por favor [**feedback**](https://github.com/linyuxuanlin/Wiki_MkDocs/issues/new) si hay alguna omisión.",
    "ar": "\n\n> تمت ترجمة هذه المشاركة باستخدام ChatGPT، يرجى [**تزويدنا بتعليقاتكم**](https://github.com/linyuxuanlin/Wiki_MkDocs/issues/new) إذا كانت هناك أي حذف أو إهمال."
}

# 文章使用英文撰写的提示，避免本身为英文的文章被重复翻译为英文
marker_written_in_en = "\n> This post was originally written in English.\n"
# 即使在已处理的列表中，仍需要重新翻译的标记
marker_force_translate = "\n[translate]\n"

# 固定字段替换规则。文章中一些固定的字段，不需要每篇都进行翻译，且翻译结果可能不一致，所以直接替换掉。
replace_rules = [
    {
        # 版权信息手动翻译
        "orginal_text": "> 原文地址：<https://wiki-power.com/>",
        "replaced_text": {
            "en": "> Original: <https://wiki-power.com/>",
            "es": "> Dirección original del artículo: <https://wiki-power.com/>",
            "ar": "> عنوان النص: <https://wiki-power.com/>",
        }
    },
    {
        # 版权信息手动翻译
        "orginal_text": "> 本篇文章受 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 协议保护，转载请注明出处。",
        "replaced_text": {
            "en": "> This post is protected by [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by/4.0/deed.en) agreement, should be reproduced with attribution.",
            "es": "> Este artículo está protegido por la licencia [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh). Si desea reproducirlo, por favor indique la fuente.",
            "ar": "> يتم حماية هذا المقال بموجب اتفاقية [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh)، يُرجى ذكر المصدر عند إعادة النشر.",
        }
    },
    {
        # 文章中的站内链接，跳转为当前相同语言的网页
        "orginal_text": "](https://wiki-power.com/",
        "replaced_text": {
            "en": "](https://wiki-power.com/en/",
            "es": "](https://wiki-power.com/es/",
            "ar": "](https://wiki-power.com/ar/",
        }
    }
    # {
    #    # 不同语言使用不同图床
    #    "orginal_text": "![](https://wiki-media-1253965369.cos.ap-guangzhou.myqcloud.com/",
    #    "replaced_en": "![](https://f004.backblazeb2.com/file/wiki-media/",
    #    "replaced_es": "![](https://f004.backblazeb2.com/file/wiki-media/",
    #    "replaced_ar": "![](https://f004.backblazeb2.com/file/wiki-media/",
    # },
]


# 定义翻译函数
def translate_text(text, lang):
    target_lang = {
        "en": "English",
        "es": "Spanish",
        "ar": "Arabic"
    }[lang]

    # 使用OpenAI API进行翻译
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"Translate the following text into {target_lang}, maintain the original markdown format.\n\n{text}\n\n\nTranslated into {target_lang}:",
            }
        ],
    )

    # 获取翻译结果
    output_text = completion.choices[0].message.content
    return output_text

# 定义翻译front_matter函数
def translate_front_matter(text, lang, param):
    target_lang = {
        "en": "English",
        "es": "Spanish",
        "ar": "Arabic",
        'cn': "Chinese"
    }[lang]

    # 使用OpenAI API进行翻译
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"Suppose the following text is a JSON format. The value of the key for ```{param}``` translates into {target_lang} and other key are not changed. maintain the original markdown format.\n\n\n{text}\n\n\nTranslated into {target_lang}:",
            }
        ],
    )

    # 获取翻译结果
    output_text = completion.choices[0].message.content
    return output_text

# 定义文章拆分函数
def split_text(text, max_length):
    # 根据段落拆分文章
    paragraphs = text.split("\n\n")
    output_paragraphs = []
    current_paragraph = ""

    for paragraph in paragraphs:
        if len(current_paragraph) + len(paragraph) + 2 <= max_length:
            # 如果当前段落加上新段落的长度不超过最大长度，就将它们合并
            if current_paragraph:
                current_paragraph += "\n\n"
            current_paragraph += paragraph
        else:
            # 否则将当前段落添加到输出列表中，并重新开始一个新段落
            output_paragraphs.append(current_paragraph)
            current_paragraph = paragraph

    # 将最后一个段落添加到输出列表中
    if current_paragraph:
        output_paragraphs.append(current_paragraph)

    # 将输出段落合并为字符串
    output_text = "\n\n".join(output_paragraphs)

    return output_text


# 定义翻译文件函数
def translate_file(input_file, filename, lang):
    print(f"Translating into {lang}: {filename}")
    sys.stdout.flush()

    # 定义输出文件
    if lang in dir_translated:
        output_dir = dir_translated[lang]
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, filename)

    # 读取输入文件内容
    with open(input_file, "r", encoding="utf-8") as f:
        input_text = f.read()
        
    # 使用正则表达式来匹配 Front Matter
    front_matter_match = re.search(r'---\n(.*?)\n---', input_text, re.DOTALL)
    if front_matter_match:
        front_matter_text = front_matter_match.group(1)
        # 使用PyYAML加载YAML格式的数据
        front_matter_data = yaml.safe_load(front_matter_text)

        # 打印front matter的参数与对应的值
        #print("Front Matter 数据:")
        for key, value in front_matter_data.items():
            if isinstance(value, bool):
                # print(f"{key}: {value}") # 打印出识别后储存的 FrontMatter 数据
                pass
            else:
                if isinstance(value, list):
                    value_str = ', '.join([f'"{v}"' for v in value])
                else:
                    value_str = f'"{value}"'
                # print(f'{key}: {value_str}') # 打印出识别后储存的 FrontMatter 数据
        # 暂时删除 Front Matter
        input_text = input_text.replace("---\n"+front_matter_text+"\n---\n", "")
        #print(front_matter_text)
        front_matter_text = translate_front_matter(front_matter_text, lang, 'title')
        #print(front_matter_text)
    else:
        #print("没有找到front matter，不进行处理。")
        pass

    # 创建一个字典来存储占位词和对应的替换文本
    placeholder_dict = {}

    # 使用 for 循环应用替换规则，并将匹配的文本替换为占位词
    for i, rule in enumerate(replace_rules):
        find_text = rule["orginal_text"]
        replace_with = rule["replaced_text"][lang]
        placeholder = f"to_be_replace[{i + 1}]"
        input_text = input_text.replace(find_text, placeholder)
        placeholder_dict[placeholder] = replace_with

    # 删除译文中指示强制翻译的 marker
    input_text = input_text.replace(marker_force_translate, "")
    
    # 删除其他出英文外其他语言译文中的 marker_written_in_en
    if lang != "en":
        input_text = input_text.replace(marker_written_in_en, "")

    # print(input_text) # debug 用，看看输入的是什么

    # 拆分文章
    paragraphs = input_text.split("\n\n")
    input_text = ""
    output_paragraphs = []
    current_paragraph = ""

    for paragraph in paragraphs:
        if len(current_paragraph) + len(paragraph) + 2 <= max_length:
            # 如果当前段落加上新段落的长度不超过最大长度，就将它们合并
            if current_paragraph:
                current_paragraph += "\n\n"
            current_paragraph += paragraph
        else:
            # 否则翻译当前段落，并将翻译结果添加到输出列表中
            output_paragraphs.append(translate_text(current_paragraph, lang))
            current_paragraph = paragraph

    # 处理最后一个段落
    if current_paragraph:
        if len(current_paragraph) + len(input_text) <= max_length:
            # 如果当前段落加上之前的文本长度不超过最大长度，就将它们合并
            input_text += "\n\n" + current_paragraph
        else:
            # 否则翻译当前段落，并将翻译结果添加到输出列表中
            output_paragraphs.append(translate_text(current_paragraph, lang))

    # 如果还有未翻译的文本，就将它们添加到输出列表中
    if input_text:
        output_paragraphs.append(translate_text(input_text, lang))

    # 将输出段落合并为字符串
    output_text = "\n\n".join(output_paragraphs)

    if front_matter_match:
        # 加入 Front Matter
        output_text = "---\n" + front_matter_text + "\n---\n\n" + output_text

    # 加入由 ChatGPT 翻译的提示
    if lang == "en":
        output_text = output_text + tips_translated_by_chatgpt["en"]
    elif lang == "es":
        output_text = output_text + tips_translated_by_chatgpt["es"]
    elif lang == "ar":
        output_text = output_text + tips_translated_by_chatgpt["ar"]
    
    # 最后，将占位词替换为对应的替换文本
    for placeholder, replacement in placeholder_dict.items():
        output_text = output_text.replace(placeholder, replacement)

    # 写入输出文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_text)

# 按文件名称顺序排序
file_list = os.listdir(dir_to_translate)
sorted_file_list = sorted(file_list)
# print(sorted_file_list)

try:
    # 创建一个外部列表文件，存放已处理的 Markdown 文件名列表
    if not os.path.exists(processed_list):
        with open(processed_list, "w", encoding="utf-8") as f:
            print("processed_list created")
            sys.stdout.flush()
    
    # 遍历目录下的所有.md文件，并进行翻译
    for filename in sorted_file_list:
        if filename.endswith(".md"):
            input_file = os.path.join(dir_to_translate, filename)

            # 读取 Markdown 文件的内容
            with open(input_file, "r", encoding="utf-8") as f:
                md_content = f.read()

            # 读取processed_list内容
            with open(processed_list, "r", encoding="utf-8") as f:
                processed_list_content = f.read()

            if marker_force_translate in md_content:  # 如果有强制翻译的标识，则执行这部分的代码
                if marker_written_in_en in md_content:  # 翻译为除英文之外的语言
                    print("Pass the en-en translation: ", filename)
                    sys.stdout.flush()
                    translate_file(input_file, filename, "es")
                    translate_file(input_file, filename, "ar")
                else:  # 翻译为所有语言
                    translate_file(input_file, filename, "en")
                    translate_file(input_file, filename, "es")
                    translate_file(input_file, filename, "ar")
            elif filename in exclude_list:  # 不进行翻译
                print(f"Pass the post in exclude_list: {filename}")
                sys.stdout.flush()
            elif filename in processed_list_content:  # 不进行翻译
                print(f"Pass the post in processed_list: {filename}")
                sys.stdout.flush()
            elif marker_written_in_en in md_content:  # 翻译为除英文之外的语言
                print(f"Pass the en-en translation: {filename}")
                sys.stdout.flush()
                for lang in ["es", "ar"]:
                    translate_file(input_file, filename, lang)
            else:  # 翻译为所有语言
                for lang in ["en", "es", "ar"]:
                    translate_file(input_file, filename, lang)

            # 将处理完成的文件名加到列表，下次跳过不处理
            if filename not in processed_list_content:
                print(f"Added into processed_list: {filename}")
                with open(processed_list, "a", encoding="utf-8") as f:
                    f.write("\n")
                    f.write(filename)

            # 强制将缓冲区中的数据刷新到终端中，使用 GitHub Action 时方便实时查看过程
            sys.stdout.flush()

except Exception as e:
    # 捕获异常并输出错误信息
    print(f"An error has occurred: {e}")
    sys.stdout.flush()
    raise SystemExit(1)  # 1 表示非正常退出，可以根据需要更改退出码
    # os.remove(input_file)  # 删除源文件
