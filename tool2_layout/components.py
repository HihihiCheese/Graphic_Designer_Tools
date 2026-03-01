"""
tool2_layout/components.py - 从秀米模板提取的 HTML 组件片段

所有 CSS 内联（微信会删 <style> 标签）
装饰图片 URL 保持秀米 CDN 原链接（xiumi.us）
"""

# ============================================================
# 通用资源 URL
# ============================================================
# 条纹装饰 PNG（新闻稿文字卡片上下边框）
STRIPE_PNG = "https://img.xiumi.us/xmi/ua/4Y1Ml/i/b919bfdc698890086535a44553ef16aa-sz_504.png"
# 半透明 GIF 分隔符（讲座模板段间分隔）
SEPARATOR_GIF = "https://statics.xiumi.us/stc/images/templates-assets/tpl-paper/image/ea21a9b4c9266fe2f1db087428f55a99-sz_11654.gif"
# 小熊 GIF（新闻稿底部分隔）
BEAR_GIF = "https://img.xiumi.us/xmi/ua/4Y1Ml/i/1d42cb068a09d4e967b1e0d817f93e08-sz_160333.gif"
# 头图 GIF（新闻稿）
HEAD_GIF = "https://img.xiumi.us/xmi/ua/4Y1Ml/i/6db0d1a138a9682746078edab9191388-sz_237778.gif"
# 尾图 GIF（新闻稿）
TAIL_GIF = "https://img.xiumi.us/xmi/ua/4Y1Ml/i/e413150e172ab498f83f0ebf3a70c63e-sz_719036.gif"


# ============================================================
# 新闻稿组件
# ============================================================

def head_image(src=None):
    """头图（全宽 GIF）"""
    url = src or HEAD_GIF
    return f'''<section style="max-width: 100%; position: static; box-sizing: border-box;">
<section style="line-height: 0; text-align: center; max-width: 100%; position: static; box-sizing: border-box;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; box-sizing: border-box;">
<img style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{url}">
</section></section></section>'''


def tail_image(src=None):
    """尾图（全宽 GIF）"""
    url = src or TAIL_GIF
    return f'''<section style="max-width: 100%; position: static; box-sizing: border-box;">
<section style="line-height: 0; text-align: center; max-width: 100%; position: static; box-sizing: border-box;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; box-sizing: border-box;">
<img style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{url}">
</section></section></section>'''


def text_card(content_html):
    """新闻稿文字卡片 — 浅蓝底 #f1f6ff + 上下条纹 PNG 装饰

    Args:
        content_html: 已格式化的段落 HTML（可包含蓝色加粗等强调标记）
    """
    stripe = f'''<section style="text-align: center; box-sizing: border-box; max-width: 100%;">
<section style="display: inline-block; width: 100%; height: 12px; vertical-align: top; overflow: hidden; background-repeat: repeat-x; background-attachment: scroll; box-sizing: border-box; background-position: 0% 0% !important; background-size: auto 100% !important; background-image: url(&quot;{STRIPE_PNG}&quot;);">
<section style="text-align: justify; box-sizing: border-box;"><p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><span style="box-sizing: border-box;"><br style="box-sizing: border-box;"></span></p></section>
</section></section>'''

    stripe_bottom = f'''<section style=" transform: perspective(0px); -webkit-transform: perspective(0px); -moz-transform: perspective(0px); -o-transform: perspective(0px); transform-style: flat; box-sizing: border-box; max-width: 100%;">
<section style="text-align: center; transform: rotateX(180deg) rotateY(180deg); -webkit-transform: rotateX(180deg) rotateY(180deg); -moz-transform: rotateX(180deg) rotateY(180deg); -o-transform: rotateX(180deg) rotateY(180deg); box-sizing: border-box;">
<section style="display: inline-block; width: 100%; height: 12px; vertical-align: top; overflow: hidden; background-repeat: repeat-x; background-attachment: scroll; box-sizing: border-box; background-position: 0% 0% !important; background-size: auto 100% !important; background-image: url(&quot;{STRIPE_PNG}&quot;);">
<section style="text-align: justify; box-sizing: border-box;"><p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><span style="box-sizing: border-box;"><br style="box-sizing: border-box;"></span></p></section>
</section></section></section>'''

    return f'''<section style="max-width: 100%; margin: 0px 0px 10px; width: 100%; box-sizing: border-box;">
<section style="text-align: left; flex-flow: row; box-sizing: border-box; max-width: 100%; width: 100%; position: static;">
<section style="display: flex; justify-content: flex-start; flex-direction: row; max-width: 100%; box-sizing: border-box;">
<section style="max-width: 100%; display: inline-block; width: 100%; flex: 0 0 auto; align-self: flex-start; vertical-align: top; box-sizing: border-box;">
<section style="display: inline-block; background-color: rgb(241, 246, 255); padding: 8px; box-sizing: border-box; width: 100%; position: static;">
<section style="box-sizing: border-box;">
{stripe}
<section style="max-width: 100%; width: 100%; box-sizing: border-box;">
<section style="flex-flow: row; box-sizing: border-box; max-width: 100%; width: 100%; position: static;">
<section style="display: flex; justify-content: flex-start; flex-direction: row; max-width: 100%; box-sizing: border-box;">
<section style="max-width: 100%; display: inline-block; width: 100%; flex: 0 0 auto; align-self: flex-start; vertical-align: top; box-sizing: border-box;">
<section style="padding: 0px 16px; box-sizing: border-box; width: 100%; position: static;">
<section style="max-width: 100%; position: static; box-sizing: border-box;">
<section style="text-align: justify; box-sizing: border-box; max-width: 100%; line-height: 1.5;">
{content_html}
</section></section></section></section></section></section></section>
{stripe_bottom}
</section></section></section></section></section></section></section>'''


def image_frame(src):
    """新闻稿图片框 — 白边 + 阴影

    Args:
        src: 图片 URL 或本地路径
    """
    return f'''<section style="max-width: 100%; margin-top: 0.5em; margin-bottom: 0.5em; box-sizing: border-box;">
<section style="line-height: 0; text-align: center; padding-left: 0.5em; padding-right: 0.5em; box-sizing: border-box; max-width: 100%; position: static;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; box-sizing: border-box; width: 100%; border: 0.3em solid white; box-shadow: rgb(102, 102, 102) 0.2em 0.2em 0.5em; height: auto;">
<img style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{src}">
</section></section></section>'''


def news_separator():
    """新闻稿底部装饰分隔线 — 蓝虚线 + 小熊 GIF"""
    return f'''<section style="position: static; max-width: 100%; margin: 10px 0px; box-sizing: border-box;">
<section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; box-sizing: border-box; max-width: 100%; position: static;">
<section style="display: inline-block; vertical-align: middle; width: auto; align-self: center; flex: 100 100 0%; height: auto; box-sizing: border-box; max-width: 100%;">
<section style="font-size: 0px; margin: 10px 0%; text-align: justify; justify-content: flex-start; display: flex; flex-flow: row; width: 100%; align-self: flex-start; background-color: rgb(171, 215, 247); box-sizing: border-box;">
<section style="margin: 0px 0%; width: 100%; box-sizing: border-box;">
<section style="border-top: 3px dashed rgb(250, 254, 255); box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float: left; line-height: 0; width: 0px; box-sizing: border-box;"></svg>
</section></section></section></section>
<section style="display: inline-block; vertical-align: middle; width: 34px; align-self: center; flex: 0 0 auto; height: auto; box-sizing: border-box; max-width: 100%;">
<section style="max-width: 100%; margin: 0px; box-sizing: border-box;">
<section style="line-height: 0; text-align: center; opacity: 0.76; box-sizing: border-box; max-width: 100%; position: static;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; width: 26px; height: auto; box-sizing: border-box;">
<img style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{BEAR_GIF}">
</section></section></section></section>
<section style="display: inline-block; vertical-align: middle; width: auto; align-self: center; flex: 100 100 0%; height: auto; box-sizing: border-box; max-width: 100%;">
<section style="font-size: 0px; margin: 10px 0%; text-align: justify; justify-content: flex-start; display: flex; flex-flow: row; width: 100%; align-self: flex-start; background-color: rgb(171, 215, 247); box-sizing: border-box;">
<section style="margin: 0px 0%; width: 100%; box-sizing: border-box;">
<section style="border-top: 3px dashed rgb(250, 254, 255); box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float: left; line-height: 0; width: 0px; box-sizing: border-box;"></svg>
</section></section></section></section>
</section></section>'''


def heading_block(text):
    """新闻稿小节标题 — 加粗居中"""
    return f'''<section style="max-width: 100%; position: static; box-sizing: border-box;">
<section style="text-align: center; font-size: 16px; box-sizing: border-box; max-width: 100%; line-height: 2;">
<p style="margin: 0px; padding: 0px; box-sizing: border-box;"><strong style="box-sizing: border-box;">{text}</strong></p>
</section></section>'''


# ============================================================
# 讲座组件
# ============================================================

def decorator_line():
    """讲座装饰线 — 蓝线 rgba(116,185,240,0.79) + 黄点 rgb(255,208,90)"""
    return '''<section style="margin: 10px 0%; display: flex; flex-flow: row; text-align: left; justify-content: flex-start; position: static; box-sizing: border-box;">
<section style="display: inline-block; vertical-align: top; width: auto; flex: 100 100 0%; height: auto; box-sizing: border-box;">
<section style="margin: 0.5em 0px; position: static; box-sizing: border-box;">
<section style="background-color: rgba(116, 185, 240, 0.79); height: 1px; box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section></section></section>
<section style="display: inline-block; vertical-align: middle; width: 25px; flex: 0 0 auto; height: auto; align-self: center; line-height: 0; padding: 0px; box-sizing: border-box;">
<section style="position: static; transform: perspective(0px); -webkit-transform: perspective(0px); transform-style: flat; box-sizing: border-box;">
<section style="text-align: center; transform: rotateX(180deg); -webkit-transform: rotateX(180deg); margin: 0px 0%; position: static; box-sizing: border-box;">
<section style="display: inline-block; width: 10px; height: 10px; vertical-align: top; overflow: hidden; border-width: 0px; border-radius: 10px; border-style: none; border-color: rgb(62, 62, 62); background-color: rgb(255, 208, 90); box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section></section></section></section>
<section style="display: inline-block; vertical-align: middle; width: auto; align-self: center; flex: 100 100 0%; height: auto; box-sizing: border-box;">
<section style="margin: 0.5em 0px; position: static; box-sizing: border-box;">
<section style="background-color: rgba(116, 185, 240, 0.79); height: 1px; box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section></section></section></section>'''


def lecture_poster(src):
    """讲座海报图片（全宽居中，无边框）"""
    return f'''<section style="text-align: center; margin-top: 10px; margin-bottom: 10px; line-height: 0; position: static; box-sizing: border-box;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; box-sizing: border-box;">
<img style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{src}">
</section></section>'''


def lecture_info(speaker, host, time, location):
    """讲座信息区 — 报告人/主持人/时间/地点（居中，标签加粗）"""
    return f'''<section style="box-sizing: border-box;">
<p style="text-align: center; white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><span style="color: rgb(0, 0, 0); box-sizing: border-box;"><strong style="box-sizing: border-box;">报告人</strong></span></p>
<p style="text-align: center; white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;">{speaker}</p>
<p style="text-align: center; white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><span style="color: rgb(0, 0, 0); box-sizing: border-box;"><strong style="box-sizing: border-box;">主持人</strong></span></p>
<p style="text-align: center; white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><span style="color: rgb(0, 0, 0); box-sizing: border-box;">{host}</span></p>
<p style="text-align: center; white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><span style="color: rgb(0, 0, 0); box-sizing: border-box;"><strong style="box-sizing: border-box;">时间</strong></span></p>
<p style="text-align: center; white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;">{time}</p>
<p style="text-align: center; white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><span style="color: rgb(0, 0, 0); box-sizing: border-box;"><strong style="box-sizing: border-box;">地点</strong></span></p>
<p style="text-align: center; white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><span style="color: rgb(0, 0, 0); box-sizing: border-box;">{location}</span></p>
</section>'''


def lecture_card(title, photo_src, abstract, bio):
    """讲座内容卡片 — 浅蓝底 #f0f4ff + 虚线框 #4f6d9b

    Args:
        title: 报告标题
        photo_src: 报告人头像 URL
        abstract: 报告摘要
        bio: 报告人简介
    """
    # 头像部分（如果有）
    photo_html = ""
    if photo_src:
        photo_html = f'''<section style="text-align: center; margin-top: 10px; margin-bottom: 10px; line-height: 0; position: static; box-sizing: border-box;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; box-sizing: border-box;">
<img style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{photo_src}">
</section></section>'''

    return f'''<section style="margin: 10px 0px; text-align: left; justify-content: flex-start; display: flex; flex-flow: row; position: static; box-sizing: border-box;">
<section style="display: inline-block; width: 100%; vertical-align: top; background-color: rgb(240, 244, 255); padding: 11px; margin: 0px; align-self: flex-start; flex: 0 0 auto; box-sizing: border-box;">
<section style="text-align: justify; justify-content: flex-start; display: flex; flex-flow: row; position: static; box-sizing: border-box;">
<section style="display: inline-block; width: 100%; vertical-align: top; border-style: dashed; border-width: 1px; border-color: rgb(79, 109, 155); padding: 27px; align-self: flex-start; flex: 0 0 auto; box-sizing: border-box;">
<section style="font-size: 18px; color: rgb(79, 109, 155); text-align: center; box-sizing: border-box;">
<p style="margin: 0px; padding: 0px; box-sizing: border-box;"><strong style="box-sizing: border-box;">{title}</strong></p>
</section>
<section style="margin: 8px 0px 18px; position: static; box-sizing: border-box;">
<section style="background-color: rgb(79, 109, 155); height: 1px; box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section></section>
{photo_html}
<section style="text-align: center; margin: 0px; position: static; box-sizing: border-box;">
<section style="text-align: justify; line-height: 1.5; box-sizing: border-box;">
<p style="text-align: center; white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><strong style="box-sizing: border-box;"><span style="color: rgb(0, 0, 0); box-sizing: border-box;">报告摘要</span></strong></p>
<p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;">{abstract}</p>
<p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p>
<p style="text-align: center; white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><strong style="box-sizing: border-box;"><span style="color: rgb(0, 0, 0); box-sizing: border-box;">报告人简介</span></strong></p>
<p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;">{bio}</p>
</section></section>
</section></section></section></section>'''


def decorator_gif():
    """讲座段间分隔 — 半透明 GIF"""
    return f'''<section style="text-align: center; margin: 10px 0%; opacity: 0.25; line-height: 0; position: static; box-sizing: border-box;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; box-sizing: border-box;">
<img style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{SEPARATOR_GIF}">
</section></section>'''


# ============================================================
# 通用组件
# ============================================================

def credits_block(credits_dict):
    """署名区域 — 12px 居中

    Args:
        credits_dict: {"美编": ["王鹏扉"], "责编": ["周芷轩"]} 这样的 dict
    """
    if not credits_dict:
        return ""
    lines = []
    for role, names in credits_dict.items():
        names_str = "、".join(names)
        lines.append(
            f'<p style="margin: 0px; padding: 0px; box-sizing: border-box;">'
            f'<span style="box-sizing: border-box;">{role} | {names_str}</span></p>'
        )
    content = "\n".join(lines)
    return f'''<section style="max-width: 100%; position: static; box-sizing: border-box;">
<section style="text-align: center; font-size: 12px; box-sizing: border-box; max-width: 100%;">
{content}
</section></section>'''


# ============================================================
# 蓝色模板2 组件（简洁短稿风格）
# 深蓝边框 rgb(71,90,171) + 浅蓝底 rgb(245,247,252) + 折角装饰
# ============================================================

# 主色调
BLUE2_PRIMARY = "rgb(71, 90, 171)"
BLUE2_BG = "rgb(245, 247, 252)"


def blue2_frame_open():
    """蓝色模板2 — 外框开始（深蓝三边边框 + 顶部折角装饰线）"""
    return f'''<section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; margin: 10px 0px; position: static; box-sizing: border-box;">
<section style="display: inline-block; width: 100%; vertical-align: top; align-self: flex-start; flex: 0 0 auto; border-style: solid; border-width: 0px 1px 1px; border-color: {BLUE2_PRIMARY}; box-sizing: border-box;">
<section style="text-align: center; justify-content: center; display: flex; flex-flow: row; margin: 0px; position: static; box-sizing: border-box;">
<section style="display: inline-block; vertical-align: bottom; width: auto; flex: 100 100 0%; height: auto; align-self: flex-end; box-sizing: border-box;">
<section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; margin: 0px; position: static; box-sizing: border-box;">
<section style="display: inline-block; width: auto; vertical-align: top; align-self: flex-start; flex: 0 0 auto; min-width: 5%; max-width: 100%; height: auto; background-color: {BLUE2_PRIMARY}; padding: 0px 7px; margin: 0px; box-sizing: border-box;">
<section style="text-align: justify; font-size: 10px; color: rgb(255, 255, 255); box-sizing: border-box;">
<p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p>
</section></section></section>
<section style="margin: 0px; position: static; box-sizing: border-box;">
<section style="background-color: {BLUE2_PRIMARY}; height: 1px; box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section></section></section>
<section style="display: inline-block; vertical-align: top; width: 30px; flex: 0 0 auto; height: auto; padding: 0px; margin: 0px -5px 0px 0px; align-self: flex-start; box-sizing: border-box;">
<section style="position: static; transform: rotateZ(315deg); -webkit-transform: rotateZ(315deg); -moz-transform: rotateZ(315deg); -o-transform: rotateZ(315deg); box-sizing: border-box;">
<section style="margin: 11px 0px 0px; position: static; box-sizing: border-box;">
<section style="background-color: {BLUE2_PRIMARY}; height: 1px; box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section></section></section></section>
<section style="display: inline-block; vertical-align: top; width: 100px; margin: 0px; flex: 0 0 auto; height: auto; align-self: flex-start; box-sizing: border-box;">
<section style="margin: 0px; position: static; box-sizing: border-box;">
<section style="background-color: {BLUE2_PRIMARY}; height: 1px; box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section></section></section></section>
<section style="justify-content: flex-start; display: flex; flex-flow: row; position: static; box-sizing: border-box;">
<section style="display: inline-block; width: 100%; vertical-align: top; align-self: flex-start; flex: 0 0 auto; background-color: {BLUE2_BG}; padding: 20px 20px 0px; box-sizing: border-box;">
<section style="justify-content: flex-start; display: flex; flex-flow: row; margin: 20px 0px; position: static; box-sizing: border-box;">
<section style="display: inline-block; vertical-align: top; width: auto; align-self: flex-start; flex: 0 0 auto; min-width: 5%; max-width: 100%; height: auto; padding: 0px 12px 0px 0px; box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section>
<section style="display: inline-block; vertical-align: top; width: auto; flex: 100 100 0%; height: auto; box-sizing: border-box;">'''


def blue2_frame_close():
    """蓝色模板2 — 外框结束"""
    return '''</section></section></section></section></section></section>'''


def blue2_image(src):
    """蓝色模板2 — 图片（无边框无阴影，直接嵌入）"""
    return f'''<section style="line-height: 0; position: static; box-sizing: border-box;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; box-sizing: border-box;">
<img style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{src}">
</section></section>'''


def blue2_paragraph(content_html):
    """蓝色模板2 — 正文段落（两端对齐，行距1.5）"""
    return f'''<section style="text-align: justify; line-height: 1.5; box-sizing: border-box;">
<p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p>
{content_html}
<p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p>
</section>'''


# ============================================================
# 红色模板组件（党建风格）
# 主色调: rgb(239,54,46) / rgb(227,36,42) / rgb(222,54,54)
# 强调色: rgb(185,27,21)  金色装饰: rgb(228,180,136)
# ============================================================

# 装饰图片 URL
RED_BANNER_PNG = "https://statics.xiumi.us/mat/i/fvId/94888a7870d9ee7d21f4956f41f566d6_sz-62219.png"
RED_RIBBON_PNG = "https://statics.xiumi.us/mat/i/fvId/983ea839a26245bdddd6284c845a3ed1_sz-11079.png"


def red_separator():
    """红色双线分隔符 — 1px 实线 + 5px 虚线，颜色 rgb(239,54,46)"""
    return '''<section style="margin: 10px 0px 0px; position: static; box-sizing: border-box;"><section style="background-color: rgb(239, 54, 46); height: 1px; box-sizing: border-box;"><svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg></section> </section><section style="margin: 0px; position: static; box-sizing: border-box;"><section style="border-top: 5px dashed rgb(239, 54, 46); box-sizing: border-box;"><svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg></section></section>'''


def red_dashed_line():
    """红色虚线 — 5px dashed rgb(239,54,46)"""
    return '''<section style="margin: 0px; position: static; box-sizing: border-box;"><section style="border-top: 5px dashed rgb(239, 54, 46); box-sizing: border-box;"><svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg></section></section>'''


def red_text_card(content_html):
    """红色边框文字卡片 — 1px solid rgb(239,54,46) + 右下角旋转方块装饰

    Args:
        content_html: 已格式化的段落 HTML（可包含红色加粗等强调标记）
    """
    return f'''<section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; margin: 0px 0px 10px; position: static; box-sizing: border-box;"><section style="display: inline-block; vertical-align: bottom; width: auto; align-self: flex-end; flex: 100 100 0%; border-style: solid; border-width: 1px; border-color: rgb(239, 54, 46); height: auto; padding: 20px; box-sizing: border-box;"><section style="margin: 0px; position: static; box-sizing: border-box;"><section style="text-align: justify; padding: 0px; line-height: 1.5; box-sizing: border-box;">{content_html}</section></section></section><section style="display: inline-block; vertical-align: bottom; width: auto; align-self: flex-end; flex: 0 0 0%; height: auto; background-color: rgb(255, 255, 255); margin: 0px -8px 0px -17px; box-sizing: border-box;"><section style="position: static; transform: rotateZ(45deg); -webkit-transform: rotateZ(45deg); -moz-transform: rotateZ(45deg); -o-transform: rotateZ(45deg); box-sizing: border-box;"><section style="text-align: center; margin: 1px 0px -9px; transform: translate3d(5px, 0px, 0px); -webkit-transform: translate3d(5px, 0px, 0px); -moz-transform: translate3d(5px, 0px, 0px); -o-transform: translate3d(5px, 0px, 0px); position: static; box-sizing: border-box;"><section class="group-empty" style="display: inline-block; width: 25px; height: 25px; vertical-align: top; overflow: hidden; border-left: 1px solid rgb(239, 54, 46); background-color: rgba(255, 255, 255, 0); box-sizing: border-box;"><svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg></section></section></section></section></section>'''


def red_activity_banner(title):
    """红色活动标题横幅 — 红底 rgb(222,54,54) 白字 + 右侧装饰 PNG 及渐变遮罩

    Args:
        title: 活动标题文字（如 "活动一：xxx"）
    """
    return f'''<section style="margin: 10px 0%; text-align: center; justify-content: center; display: flex; flex-flow: row; position: static; box-sizing: border-box;"><section style="display: inline-block; width: auto; vertical-align: top; background-color: rgb(222, 54, 54); border-width: 0px;  border-style: none; border-color: rgb(62, 62, 62); overflow: hidden; min-width: 10%; max-width: 100%; flex: 0 0 auto; height: auto; align-self: flex-start; box-sizing: border-box;"><section style="display: flex; flex-flow: row; justify-content: center; position: static; box-sizing: border-box;"><section style="display: inline-block; vertical-align: middle; width: auto; flex: 100 100 0%; align-self: center; height: auto; margin: 0px -80px 0px 0px; z-index: 1; box-sizing: border-box;"><section style=" transform: translate3d(20px, 0px, 0px); -webkit-transform: translate3d(20px, 0px, 0px); -moz-transform: translate3d(20px, 0px, 0px); -o-transform: translate3d(20px, 0px, 0px); position: static; box-sizing: border-box;"><section style="color: rgb(255, 243, 243); line-height: 1.6; letter-spacing: 1px; box-sizing: border-box;"><p style="margin: 0px; padding: 0px; box-sizing: border-box;"><strong style="box-sizing: border-box;">{title}</strong></p></section></section></section><section style="display: inline-block; vertical-align: top; width: 128px; height: auto; flex: 0 0 auto; align-self: flex-start; box-sizing: border-box;"><section style="margin: -34px 0% 0px; transform: translate3d(20px, 0px, 0px); -webkit-transform: translate3d(20px, 0px, 0px); -moz-transform: translate3d(20px, 0px, 0px); -o-transform: translate3d(20px, 0px, 0px); line-height: 0; position: static; box-sizing: border-box;"><section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; box-sizing: border-box;"><img class="raw-image" style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{RED_BANNER_PNG}"></section></section><section style="margin: -50px 0% 0px; transform: translate3d(1px, 0px, 0px); -webkit-transform: translate3d(1px, 0px, 0px); -moz-transform: translate3d(1px, 0px, 0px); -o-transform: translate3d(1px, 0px, 0px); position: static; box-sizing: border-box;"><section class="group-empty" style="display: inline-block; width: 100%; height: 55px; vertical-align: top; overflow: hidden; background-image: linear-gradient(to left bottom, rgba(222, 54, 53, 0) 0%, rgb(222, 54, 53) 100%); box-sizing: border-box;"><svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg></section></section></section></section></section></section>'''


def red_numbered_heading(number, title):
    """红色编号小标题 — 红底 rgb(227,36,42) + 金色圆圈编号 rgb(228,180,136) + 两侧金色三角装饰

    Args:
        number: 编号数字（如 1, 2, 3）
        title: 小标题文字
    """
    return f'''<section style="text-align: center; justify-content: center; display: flex; flex-flow: row; margin: 10px 0px 0px; transform: translate3d(-1px, 0px, 0px); -webkit-transform: translate3d(-1px, 0px, 0px); -moz-transform: translate3d(-1px, 0px, 0px); -o-transform: translate3d(-1px, 0px, 0px); position: static; box-sizing: border-box;"><section style="display: inline-block; vertical-align: bottom; width: auto; min-width: 5%; max-width: 100%; flex: 0 0 auto; height: auto; align-self: flex-end; box-sizing: border-box;"><section style="position: static; transform: perspective(0px); -webkit-transform: perspective(0px); -moz-transform: perspective(0px); -o-transform: perspective(0px); transform-style: flat; box-sizing: border-box;"><section style="text-align: right; transform: rotateX(180deg); -webkit-transform: rotateX(180deg); -moz-transform: rotateX(180deg); -o-transform: rotateX(180deg); position: static; box-sizing: border-box;"><section style="display: inline-block; width: 14px; height: 14px; vertical-align: top; overflow: hidden; background-color: rgb(228, 180, 136); box-sizing: border-box;"><section style="text-align: justify; box-sizing: border-box;"><p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p></section></section></section></section></section><section style="display: inline-block; vertical-align: bottom; width: auto; align-self: flex-end; flex: 0 0 auto; background-color: rgb(227, 36, 42); min-width: 5%; max-width: 100%; height: auto; padding: 4px 10px; box-sizing: border-box;"><section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; position: static; box-sizing: border-box;"><section style="display: inline-block; vertical-align: middle; width: auto; min-width: 5%; max-width: 100%; flex: 0 0 auto; height: auto; align-self: center; box-sizing: border-box;"><section style="font-size: 19px; margin: 0px 0%; text-align: center; position: static; box-sizing: border-box;"><section style="display: inline-block; border: 1px solid rgb(228, 180, 136); background-color: rgb(228, 180, 136); width: 1.8em; height: 1.8em; line-height: 1.8em; border-radius: 100%; margin-left: auto; margin-right: auto; font-size: 15px; color: rgb(255, 255, 255); box-sizing: border-box;"><p style="margin: 0px; padding: 0px; box-sizing: border-box;">{number}</p></section></section></section><section style="display: inline-block; vertical-align: middle; width: auto; min-width: 5%; max-width: 100%; flex: 0 0 auto; height: auto; align-self: center; padding: 0px 0px 0px 10px; box-sizing: border-box;"><section style="text-align: justify; color: rgb(255, 255, 255); box-sizing: border-box;"><p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><strong style="box-sizing: border-box;">{title}</strong></p></section></section></section></section><section style="display: inline-block; vertical-align: bottom; width: auto; min-width: 5%; max-width: 100%; flex: 0 0 auto; height: auto; align-self: flex-end; box-sizing: border-box;"><section style="position: static; transform: perspective(0px); -webkit-transform: perspective(0px); -moz-transform: perspective(0px); -o-transform: perspective(0px); transform-style: flat; box-sizing: border-box;"><section style="text-align: left; transform: rotateX(180deg); -webkit-transform: rotateX(180deg); -moz-transform: rotateX(180deg); -o-transform: rotateX(180deg); position: static; box-sizing: border-box;"><section style="display: inline-block; width: 14px; height: 14px; vertical-align: top; overflow: hidden; background-color: rgb(228, 180, 136); box-sizing: border-box;"><section style="text-align: justify; box-sizing: border-box;"><p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p></section></section></section></section></section></section>'''


def red_text_block(content_html):
    """红色边框正文块 — 2px solid rgb(227,36,42)，内边距 21px，两端对齐，行距 1.5

    Args:
        content_html: 已格式化的段落 HTML
    """
    return f'''<section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; margin: 0px 0px 10px; width: 100%; align-self: flex-start; padding: 21px; border-style: solid; border-width: 2px; border-color: rgb(227, 36, 42); position: static; box-sizing: border-box;"><section style="margin: 0px; text-align: center; width: 100%; position: static; box-sizing: border-box;"><section style="text-align: justify; line-height: 1.5; width: 100%; box-sizing: border-box;">{content_html}</section></section></section>'''


def red_image(src):
    """红色模板普通图片 — 无装饰，全宽显示

    Args:
        src: 图片 URL
    """
    return f'''<section style="line-height: 0; position: static; box-sizing: border-box;"><section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; box-sizing: border-box;"><img class="raw-image" style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{src}"></section></section>'''


def red_image_with_ribbon(src):
    """红色模板图片 + 右侧红色书签丝带装饰 PNG（23px 宽）

    Args:
        src: 图片 URL
    """
    return f'''<section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; margin: 10px 0px; position: static; box-sizing: border-box;"><section style="display: inline-block; vertical-align: bottom; width: auto; align-self: flex-end; flex: 100 100 0%; height: auto; box-sizing: border-box;"><section style="margin: 0px; line-height: 0; position: static; box-sizing: border-box;"><section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; width: 100%; height: auto; box-sizing: border-box;"><img class="raw-image" style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{src}"></section></section></section><section style="display: inline-block; vertical-align: bottom; width: 59px; align-self: flex-end; flex: 0 0 auto; height: auto; box-sizing: border-box;"><section style="text-align: center; margin: 0px; line-height: 0; position: static; box-sizing: border-box;"><section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; width: 23px; height: auto; box-sizing: border-box;"><img class="raw-image" style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{RED_RIBBON_PNG}"></section></section></section></section>'''


def red_image_with_bar(src):
    """红色模板图片 + 左侧竖条装饰（7px 宽，rgba(219,66,49,0.13)，高 100px）

    Args:
        src: 图片 URL
    """
    return f'''<section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; margin: 10px 0px; position: static; box-sizing: border-box;"><section style="display: inline-block; vertical-align: top; width: 10%; align-self: flex-start; flex: 0 0 auto; height: auto; box-sizing: border-box;"><section style="text-align: center; position: static; box-sizing: border-box;"><section style="display: inline-block; width: 7px; height: 100px; vertical-align: top; overflow: hidden; background-color: rgba(219, 66, 49, 0.13); box-sizing: border-box;"><section style="text-align: justify; box-sizing: border-box;"><p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p></section></section></section></section><section style="display: inline-block; vertical-align: top; width: auto; flex: 100 100 0%; height: auto; box-sizing: border-box;"><section style="text-align: center; margin: 0px; line-height: 0; position: static; box-sizing: border-box;"><section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; width: 100%; height: auto; box-sizing: border-box;"><img class="raw-image" style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{src}"></section></section></section></section>'''


# ============================================================
# 青色模板组件（学术论坛风格）
# 渐变: linear-gradient(45deg, rgb(0,220,253) 13%, rgb(4,104,255) 88%)
# 边框: rgb(22,151,255)  橙色徽章: rgb(255,96,20)
# 浅青背景: rgba(0,220,253,0.07)
# ============================================================

CYAN_GRADIENT = "linear-gradient(45deg, rgb(0, 220, 253) 13%, rgb(4, 104, 255) 88%)"
CYAN_BORDER = "rgb(22, 151, 255)"
CYAN_ORANGE = "rgb(255, 96, 20)"
CYAN_BG = "rgba(0, 220, 253, 0.07)"


def cyan_text_card(content_html):
    """青色文字卡片 — 蓝色圆角边框 + 两侧渐变竖条装饰

    用于导语/结语等重点段落。

    Args:
        content_html: 已格式化的段落 HTML
    """
    sidebar = f'''<section style="display: inline-block; vertical-align: middle; width: auto; flex: 0 0 0%; height: auto; align-self: center; box-sizing: border-box;">
<section style="text-align: center; position: static; box-sizing: border-box;">
<section style="display: inline-block; width: 6px; height: 75px; vertical-align: top; overflow: hidden; background-image: {CYAN_GRADIENT}; border-style: solid; border-width: 0px; box-sizing: border-box;">
<section style="text-align: justify; box-sizing: border-box;"><p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p></section>
</section></section></section>'''

    return f'''<section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; margin: 10px 0px; position: static; box-sizing: border-box;">
<section style="display: inline-block; width: auto; vertical-align: bottom; align-self: flex-end; flex: 100 100 0%; border-style: solid; border-width: 1px; border-color: {CYAN_BORDER}; border-radius: 12px; overflow: hidden; padding: 12px 0px; height: auto; margin: 0px; box-sizing: border-box;">
<section style="justify-content: flex-start; display: flex; flex-flow: row; position: static; box-sizing: border-box;">
{sidebar}
<section style="display: inline-block; vertical-align: middle; width: auto; align-self: center; flex: 100 100 0%; height: auto; padding: 0px 13px; box-sizing: border-box;">
<section style="text-align: justify; line-height: 1.5; box-sizing: border-box;">
{content_html}
</section></section>
{sidebar}
</section></section></section>'''


def cyan_numbered_heading(number, title):
    """青色编号标题 — 橙色半圆徽章 + 渐变药丸标签

    Args:
        number: 编号数字
        title: 标题文字
    """
    return f'''<section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; margin: 10px 0px; position: static; box-sizing: border-box;">
<section style="display: inline-block; vertical-align: middle; width: auto; align-self: center; flex: 0 0 auto; min-width: 5%; max-width: 100%; height: auto; margin: 0px -17px 0px 0px; box-sizing: border-box;">
<section style="display: flex; width: 100%; flex-flow: column; box-sizing: border-box;">
<section style="position: static; z-index: 1; box-sizing: border-box;">
<section style="position: static; box-sizing: border-box;">
<section style="display: inline-block; width: 27px; height: 27px; vertical-align: top; overflow: hidden; background-color: {CYAN_ORANGE}; border-top-right-radius: 29px; border-bottom-right-radius: 29px; border-style: solid; border-width: 2px; border-color: rgb(255, 255, 255); box-sizing: border-box;">
<section style="text-align: center; transform: translate3d(-2px, 0px, 0px); -webkit-transform: translate3d(-2px, 0px, 0px); -moz-transform: translate3d(-2px, 0px, 0px); -o-transform: translate3d(-2px, 0px, 0px); position: static; box-sizing: border-box;">
<section style="color: rgb(255, 255, 255); line-height: 1.4; box-sizing: border-box;">
<p style="margin: 0px; padding: 0px; box-sizing: border-box;"><strong style="box-sizing: border-box;">{number}</strong></p>
</section></section></section></section></section></section></section>
<section style="display: inline-block; vertical-align: middle; width: auto; align-self: center; flex: 0 0 auto; min-width: 5%; max-width: 100%; height: auto; padding: 7px 8px; border-top-right-radius: 47px; overflow: hidden; background-image: {CYAN_GRADIENT}; border-bottom-right-radius: 47px; box-sizing: border-box;">
<section style="justify-content: flex-start; display: flex; flex-flow: row; position: static; box-sizing: border-box;">
<section style="display: inline-block; width: auto; vertical-align: middle; align-self: center; flex: 0 0 auto; min-width: 5%; max-width: 100%; height: auto; padding: 0px 12px 0px 20px; box-sizing: border-box;">
<section style="text-align: justify; color: rgb(255, 255, 255); box-sizing: border-box;">
<p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><b style="box-sizing: border-box;">{title}</b></p>
</section></section></section></section></section>'''


def cyan_text_block(content_html):
    """青色正文块 — 浅青色背景 + 20px 内边距

    Args:
        content_html: 已格式化的段落 HTML
    """
    return f'''<section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; margin: 10px 0px; width: 100%; align-self: flex-start; background-color: {CYAN_BG}; padding: 20px; position: static; box-sizing: border-box;">
<section style="text-align: justify; width: 100%; box-sizing: border-box;">
{content_html}
</section></section>'''


def cyan_image(src):
    """青色模板图片 — 全宽无边框

    Args:
        src: 图片 URL
    """
    return f'''<section style="line-height: 0; position: static; box-sizing: border-box;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; box-sizing: border-box;">
<img class="raw-image" style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{src}">
</section></section>'''


def cyan_credits(credits_dict):
    """青色模板署名区域 — 12px 居中

    Args:
        credits_dict: {"美编": ["xxx"], "责编": ["xxx"]}
    """
    if not credits_dict:
        return ""
    lines = []
    for role, names in credits_dict.items():
        if isinstance(names, list):
            names_str = "、".join(names)
        else:
            names_str = names
        lines.append(
            f'<p style="margin: 0px; padding: 0px; box-sizing: border-box;">'
            f'<span style="box-sizing: border-box;">{role} | {names_str}</span></p>'
        )
    content = "\n".join(lines)
    return f'''<section style="max-width: 100%; position: static; box-sizing: border-box;">
<section style="text-align: center; font-size: 12px; box-sizing: border-box; max-width: 100%;">
{content}
</section></section>'''


def red_credits(credits_dict):
    """红色模板署名区域 — 14px 灰色 rgb(160,160,160) 居中

    Args:
        credits_dict: {"供稿": "xxx", "图文作者": "xxx", "审核": "xxx", "美编": "xxx", "责编": "xxx"}
                      值可以是字符串或列表
    """
    if not credits_dict:
        return ""
    lines = []
    for role, names in credits_dict.items():
        if isinstance(names, list):
            names_str = " ".join(names)
        else:
            names_str = names
        lines.append(
            f'<p style="text-align: center; white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;">'
            f'<span style="color: rgb(160, 160, 160); font-size: 14px; box-sizing: border-box;">'
            f'{role} | {names_str}</span></p>'
        )
    content = "\n".join(lines)
    return f'''<section style="box-sizing: border-box;">
<p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p>
{content}
</section>'''


# ============================================================
# 红色模板2 组件（党建简约风格）
# 主色调: rgb(216,23,23)  浅红边框: rgba(216,23,23,0.1)
# 菱形点: rgb(216,2,2)
# ============================================================

# 装饰图片 URL
RED2_CORNER_GIF = "https://statics.xiumi.us/stc/images/templates-assets/tpl-paper/image/81c4a3c12b17c040b6e9426b5fe58591-sz_1834879.gif"
RED2_TITLE_PNG = "https://statics.xiumi.us/mat/i/fvId/5bdb7ea8a661cad17f250ac98251ab2a_sz-5654.png?x-oss-process=image/contrast,10"
RED2_CORNER_BOTTOM_PNG = "https://statics.xiumi.us/mat/i/fvId/d7215dafe0731d95a9d855e0bfca223d_sz-17127.png"


def red2_frame_open():
    """红色模板2 — 外框开始（左上角 GIF + 红色边框）"""
    return f'''<section style="text-align: left; margin: 10px 0px -9px; line-height: 0; transform: translate3d(20px, 0px, 0px); -webkit-transform: translate3d(20px, 0px, 0px); -moz-transform: translate3d(20px, 0px, 0px); -o-transform: translate3d(20px, 0px, 0px); position: static; box-sizing: border-box;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; width: 65px; height: auto; box-sizing: border-box;">
<img class="raw-image" style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{RED2_CORNER_GIF}">
</section></section>
<section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; position: static; box-sizing: border-box;">
<section style="display: inline-block; width: auto; vertical-align: top; align-self: flex-start; flex: 100 100 0%; border-style: solid; border-width: 2px; border-color: rgb(216, 23, 23); height: auto; margin: 0px 10px; padding: 20px 25px; box-sizing: border-box;">
<section style="display: flex; width: 100%; flex-flow: column; box-sizing: border-box;">
<section style="position: static; z-index: 1; box-sizing: border-box;">
<section style="text-align: center; margin: 0px 0px 10px; line-height: 0; position: static; box-sizing: border-box;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; width: 200px; height: auto; box-sizing: border-box;">
<img class="raw-image" style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{RED2_TITLE_PNG}">
</section></section></section></section>'''


def red2_frame_close():
    """红色模板2 — 外框结束（右下角装饰 PNG）"""
    return f'''</section></section>
<p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p>
<section style="text-align: right; margin: -41px 0px 10px; line-height: 0; transform: translate3d(7px, 0px, 0px); -webkit-transform: translate3d(7px, 0px, 0px); -moz-transform: translate3d(7px, 0px, 0px); -o-transform: translate3d(7px, 0px, 0px); position: static; box-sizing: border-box;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; width: 120px; height: auto; box-sizing: border-box;">
<img class="raw-image" style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{RED2_CORNER_BOTTOM_PNG}">
</section></section>'''


def red2_paragraph(content_html):
    """红色模板2 — 正文段落（两端对齐，行距 1.5）

    Args:
        content_html: 已格式化的段落 HTML
    """
    return f'''<section style="text-align: justify; line-height: 1.5; box-sizing: border-box;">
<p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p>
{content_html}
<p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p>
</section>'''


def red2_image(src):
    """红色模板2 — 图片（浅红色 12px 宽边框）

    Args:
        src: 图片 URL
    """
    return f'''<section style="text-align: center; margin-top: 10px; margin-bottom: 10px; line-height: 0; position: static; box-sizing: border-box;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; border-style: solid; border-width: 12px; border-color: rgba(216, 23, 23, 0.1); box-sizing: border-box;">
<img class="raw-image" style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{src}">
</section></section>'''


def red2_diamond_separator():
    """红色模板2 — 菱形点分隔符（三个红色菱形 + 两个红色圆点）"""
    return '''<section style="text-align: center; justify-content: center; display: flex; flex-flow: row; margin: 10px 0px; position: static; box-sizing: border-box;">
<section style="display: inline-block; vertical-align: middle; width: auto; align-self: center; flex: 0 0 0%; height: auto; line-height: 0; padding: 0px 4px; box-sizing: border-box;">
<section style="position: static; transform: rotateZ(45deg); -webkit-transform: rotateZ(45deg); -moz-transform: rotateZ(45deg); -o-transform: rotateZ(45deg); box-sizing: border-box;">
<section style="position: static; box-sizing: border-box;">
<section class="group-empty" style="display: inline-block; width: 6px; height: 6px; vertical-align: top; overflow: hidden; background-color: rgb(216, 2, 2); box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section></section></section></section>
<section style="display: inline-block; vertical-align: middle; width: auto; align-self: center; flex: 0 0 0%; height: auto; line-height: 0; padding: 0px 4px; box-sizing: border-box;">
<section style="position: static; box-sizing: border-box;">
<section class="group-empty" style="display: inline-block; width: 4px; height: 4px; vertical-align: top; overflow: hidden; border-width: 0px; border-radius: 100%; border-style: none; border-color: rgb(62, 62, 62); background-color: rgb(216, 2, 2); box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section></section></section>
<section style="display: inline-block; vertical-align: middle; width: auto; align-self: center; flex: 0 0 0%; height: auto; line-height: 0; padding: 0px 4px; box-sizing: border-box;">
<section style="position: static; transform: rotateZ(45deg); -webkit-transform: rotateZ(45deg); -moz-transform: rotateZ(45deg); -o-transform: rotateZ(45deg); box-sizing: border-box;">
<section style="position: static; box-sizing: border-box;">
<section class="group-empty" style="display: inline-block; width: 6px; height: 6px; vertical-align: top; overflow: hidden; background-color: rgb(216, 2, 2); box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section></section></section></section>
<section style="display: inline-block; vertical-align: middle; width: auto; align-self: center; flex: 0 0 0%; height: auto; line-height: 0; padding: 0px 4px; box-sizing: border-box;">
<section style="position: static; box-sizing: border-box;">
<section class="group-empty" style="display: inline-block; width: 4px; height: 4px; vertical-align: top; overflow: hidden; border-width: 0px; border-radius: 100%; border-style: none; border-color: rgb(62, 62, 62); background-color: rgb(216, 2, 2); box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section></section></section>
<section style="display: inline-block; vertical-align: middle; width: auto; align-self: center; flex: 0 0 0%; height: auto; line-height: 0; padding: 0px 4px; box-sizing: border-box;">
<section style="position: static; transform: rotateZ(45deg); -webkit-transform: rotateZ(45deg); -moz-transform: rotateZ(45deg); -o-transform: rotateZ(45deg); box-sizing: border-box;">
<section style="position: static; box-sizing: border-box;">
<section class="group-empty" style="display: inline-block; width: 6px; height: 6px; vertical-align: top; overflow: hidden; background-color: rgb(216, 2, 2); box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section></section></section></section></section>'''


def red2_credits(credits_dict):
    """红色模板2 署名区域 — 12px 居中

    Args:
        credits_dict: {"文字": "xxx", "图片": "xxx", "审核": "xxx", ...}
    """
    if not credits_dict:
        return ""
    lines = []
    for role, names in credits_dict.items():
        if isinstance(names, list):
            names_str = " ".join(names)
        else:
            names_str = names
        lines.append(
            f'<p style="text-align: center; white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;">'
            f'{role} | {names_str}</p>'
        )
    content = "\n".join(lines)
    return f'''<section style="font-size: 12px; box-sizing: border-box;">
{content}
</section>'''


# ============================================================
# 紫色模板组件（正式通知/会议风格）
# 渐变: linear-gradient(90deg, rgb(77,0,153) 0%, rgb(147,48,195) 100%)
# 浅紫背景: rgb(248,242,255)  分隔线: rgb(227,205,253)
# 强调色: rgb(77,0,153)
# ============================================================

PURPLE_GRADIENT = "linear-gradient(90deg, rgb(77, 0, 153) 0%, rgb(147, 48, 195) 100%)"
PURPLE_BG = "rgb(248, 242, 255)"
PURPLE_LINE_COLOR = "rgb(227, 205, 253)"
PURPLE_ACCENT = "rgb(147, 48, 195)"
PURPLE_SEPARATOR_ICON = "https://statics.xiumi.us/mat/i/fvId/29ca2fd9d2868b5c743b3c179811b2ba_sz-30278.png"


def purple_heading(title):
    """紫色标题栏 — 渐变背景 + 白色加粗文字 18px + 右侧装饰方块

    Args:
        title: 标题文字（如 "一、会议主题"）
    """
    return f'''<section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; margin: 10px 0px 0px; position: static; box-sizing: border-box;">
<section style="display: inline-block; vertical-align: top; width: auto; align-self: stretch; flex: 100 100 0%; background-image: {PURPLE_GRADIENT}; height: auto; padding: 0px 8px 0px 9px; margin: 0px; box-sizing: border-box;">
<section style="text-align: justify; color: rgb(255, 255, 255); font-size: 18px; box-sizing: border-box;">
<p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><strong style="box-sizing: border-box;">{title}</strong></p>
</section></section>
<section style="display: inline-block; vertical-align: top; width: auto; min-width: 5%; max-width: 100%; flex: 0 0 auto; height: auto; box-sizing: border-box;">
<section style="text-align: center; justify-content: center; display: flex; flex-flow: row; margin: 0px; position: static; box-sizing: border-box;">
<section style="display: inline-block; width: auto; vertical-align: bottom; line-height: 0; min-width: 5%; max-width: 100%; flex: 0 0 auto; height: auto; align-self: flex-end; margin: 0px; box-sizing: border-box;">
<section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; position: static; box-sizing: border-box;">
<section style="display: inline-block; vertical-align: bottom; width: auto; min-width: 5%; max-width: 100%; flex: 0 0 auto; height: auto; align-self: flex-end; box-sizing: border-box;">
<section style="text-align: center; position: static; box-sizing: border-box;">
<section style="display: inline-block; width: 9px; height: 9px; vertical-align: top; overflow: hidden; background-color: {PURPLE_ACCENT}; box-sizing: border-box;">
<section style="text-align: justify; box-sizing: border-box;"><p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p></section>
</section></section></section>
<section style="display: inline-block; vertical-align: bottom; width: auto; min-width: 5%; max-width: 100%; flex: 0 0 auto; height: auto; align-self: flex-end; padding: 0px 0px 0px 9px; box-sizing: border-box;">
<section style="text-align: center; position: static; box-sizing: border-box;">
<section style="display: inline-block; width: 7px; height: 7px; vertical-align: top; overflow: hidden; background-color: {PURPLE_ACCENT}; box-sizing: border-box;">
<section style="text-align: justify; box-sizing: border-box;"><p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p></section>
</section></section></section>
<section style="display: inline-block; vertical-align: bottom; width: auto; min-width: 5%; max-width: 100%; flex: 0 0 auto; height: auto; align-self: flex-end; padding: 0px 0px 0px 9px; box-sizing: border-box;">
<section style="text-align: center; position: static; box-sizing: border-box;">
<section style="display: inline-block; width: 5px; height: 5px; vertical-align: top; overflow: hidden; background-color: {PURPLE_ACCENT}; box-sizing: border-box;">
<section style="text-align: justify; box-sizing: border-box;"><p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;"><br style="box-sizing: border-box;"></p></section>
</section></section></section>
</section></section></section></section></section>'''


def purple_text_block(content_html):
    """紫色正文块 — 浅紫背景 rgb(248,242,255) + 19px 内边距

    Args:
        content_html: 已格式化的段落 HTML
    """
    return f'''<section style="text-align: left; justify-content: flex-start; display: flex; flex-flow: row; margin: 0px 0px 10px; width: 100%; align-self: flex-start; background-color: {PURPLE_BG}; padding: 19px; position: static; box-sizing: border-box;">
<section style="text-align: justify; color: rgb(0, 0, 0); width: 100%; line-height: 1.5; box-sizing: border-box;">
{content_html}
</section></section>'''


def purple_image(src):
    """紫色模板图片 — 全宽无边框

    Args:
        src: 图片 URL
    """
    return f'''<section style="line-height: 0; position: static; box-sizing: border-box;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; box-sizing: border-box;">
<img class="raw-image" style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{src}">
</section></section>'''


def purple_separator():
    """紫色分隔线 — 浅紫线 rgb(227,205,253) + 中间紫色图标"""
    return f'''<section style="text-align: center; justify-content: center; margin: 10px 0%; display: flex; flex-flow: row; position: static; box-sizing: border-box;">
<section style="display: inline-block; vertical-align: middle; width: auto; flex: 100 100 0%; align-self: center; height: auto; box-sizing: border-box;">
<section style="margin: 0px 0%; position: static; box-sizing: border-box;">
<section style="background-color: {PURPLE_LINE_COLOR}; height: 1px; box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section></section></section>
<section style="display: inline-block; vertical-align: middle; width: auto; min-width: 5%; max-width: 100%; flex: 0 0 auto; height: auto; align-self: center; margin: 0px 15px; box-sizing: border-box;">
<section style="margin: 0px; line-height: 0; position: static; box-sizing: border-box;">
<section style="max-width: 100%; vertical-align: middle; display: inline-block; line-height: 0; width: 31px; height: auto; box-sizing: border-box;">
<img class="raw-image" style="vertical-align: middle; max-width: 100%; width: 100%; box-sizing: border-box;" src="{PURPLE_SEPARATOR_ICON}">
</section></section></section>
<section style="display: inline-block; vertical-align: middle; width: auto; flex: 100 100 0%; align-self: center; height: auto; box-sizing: border-box;">
<section style="margin: 0px 0%; position: static; box-sizing: border-box;">
<section style="background-color: {PURPLE_LINE_COLOR}; height: 1px; box-sizing: border-box;">
<svg viewBox="0 0 1 1" style="float:left;line-height:0;width:0;vertical-align:top;"></svg>
</section></section></section></section>'''


def purple_credits(credits_dict):
    """紫色模板署名区域 — 12px 居中

    Args:
        credits_dict: {"美编": ["xxx"], "责编": ["xxx"]}
    """
    if not credits_dict:
        return ""
    lines = []
    for role, names in credits_dict.items():
        if isinstance(names, list):
            names_str = "、".join(names)
        else:
            names_str = names
        lines.append(
            f'<p style="margin: 0px; padding: 0px; box-sizing: border-box;">'
            f'{role} | {names_str}</p>'
        )
    content = "\n".join(lines)
    return f'''<section style="text-align: center; font-size: 12px; box-sizing: border-box;">
{content}
</section>'''
