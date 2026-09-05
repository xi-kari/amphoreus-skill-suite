#!/usr/bin/env python3
"""Validate the flat Amphoreus skill family without running model behavior."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


HEROES = (
    "aglaea",
    "tribbie",
    "mydei",
    "castorice",
    "anaxa",
    "hyacine",
    "cipher",
    "cerydra",
    "hysilens",
    "march7th",
    "terrae",
    "phainon",
    "cyrene",
)

WAVES = {
    "0": ("anaxa",),
    "1": ("anaxa", "hyacine", "phainon", "march7th"),
    "2": ("anaxa", "hyacine", "phainon", "march7th", "aglaea", "cerydra", "terrae"),
    "3": (
        "anaxa",
        "hyacine",
        "phainon",
        "march7th",
        "aglaea",
        "cerydra",
        "terrae",
        "mydei",
        "cipher",
        "castorice",
        "hysilens",
    ),
    "4": HEROES,
    "all": HEROES,
}

ROUTER_SECTIONS = (
    "核心承诺",
    "必读分层",
    "分派表",
    "流水线与会诊",
    "档位与降档",
    "输出契约",
    "常见错误",
)

CARD_SECTIONS = (
    "身份与职能",
    "方法论步骤",
    "话术契约",
    "输出模板",
    "协作与移交",
    "影子自检与停止条件",
    "常见错误",
)

EVAL_PREFIX = {
    "aglaea": "AGLAEA",
    "tribbie": "TRIBBIE",
    "mydei": "MYDEI",
    "castorice": "CASTORICE",
    "anaxa": "ANAXA",
    "hyacine": "HYACINE",
    "cipher": "CIPHER",
    "cerydra": "CERYDRA",
    "hysilens": "HYSILENS",
    "march7th": "MARCH7TH",
    "terrae": "TERRAE",
    "phainon": "PHAINON",
    "cyrene": "CYRENE",
}

UNFINISHED = re.compile(
    r"\b(?:TODO|TBD|PLACEHOLDER)\b|待补|待定稿|稍后填写|implement later|fill in details",
    re.IGNORECASE,
)

LEGACY_SKILL_REF = re.compile(
    r"cyrene-voice-lab"
    r"|\$cyrene\b"
    r"|(?:skills?|\.\.)[\\/]cyrene(?:[\\/]|$)"
    r"|\]\([^\n)]*(?<!amphoreus-)cyrene(?:[\\/][^\n)]*)?\)"
    r"|`(?:skill\s*:\s*)?cyrene`",
    re.IGNORECASE,
)

BAD_VOICE_GROUP_SEPARATOR = re.compile(r"(?:队伍编成|关于自己|关于角色|关于同伴)·")
EXPECTED_VOICE_GROUPS_BY_HERO = {
    "mydei": {
        "sr:character-voice:9c95a81ec8305dc27bf55cfb": "初次见面", "sr:character-voice:46aba8bec22864bfd1f374a1": "问候", "sr:character-voice:32a46c409d22849af0046169": "关于自己•过去", "sr:character-voice:7d1bdb3975985664db538abd": "关于阿格莱雅", "sr:character-voice:a1c6a766e0df2d5b39442d81": "关于缇宝•缇安•缇宁", "sr:character-voice:7c48583961af964150dcd637": "关于白厄", "sr:character-voice:4b04d17a25cc1ed65f55d5b6": "关于风堇", "sr:character-voice:348176402aa5bdc6256ac1e6": "关于三月七", "sr:character-voice:260317d85498757dabce1f68": "角色满级", "sr:character-voice:385c6e14c418b3531398302c": "队伍编成•开拓者", "sr:character-voice:c6b4ac4241dfc32383a43175": "队伍编成•风堇", "sr:character-voice:d765904098c167ef961027eb": "队伍编成•白厄", "sr:character-voice:e053556d6f7fee81877431fe": "队伍编成•三月七", "sr:character-voice:cba134a60c8751206cf44226": "重回战斗", "sr:character-voice:0028b1f20e4d887d1d8b0d3c": "战斗胜利", "sr:character-voice:b96654664900d6603656aa6a": "解谜成功•二",
    },
    "cipher": {
        "sr:character-voice:532ec18f04582021ea3f0ea5": "初次见面", "sr:character-voice:bc9f080ad1401e2b34615372": "问候", "sr:character-voice:f87a3bb052154bfdab695ae1": "道别", "sr:character-voice:bf7ef039cace503167831682": "关于自己•身份", "sr:character-voice:a5a5ac0e4ad76c0c7b63c0b1": "闲谈•工具", "sr:character-voice:cc6cfda976fa2b4021ac5a05": "见闻", "sr:character-voice:0c2ed07e09aad95997793fda": "关于缇宝•缇安•缇宁", "sr:character-voice:05d42bfba05e039498526835": "关于遐蝶", "sr:character-voice:1aee6338271aeb9f45681263": "星魂激活", "sr:character-voice:1b26b6725437319ee97a8d20": "角色晋阶", "sr:character-voice:e61e259fd78fc2409b7dbaa2": "队伍编成•阿格莱雅", "sr:character-voice:56d22afa023adf00a590641b": "队伍编成•遐蝶", "sr:character-voice:8404f4f31e07e17e8aa8787f": "队伍编成•缇宝", "sr:character-voice:eb9246b2e0e763c6ea5bcb1e": "队伍编成•那刻夏",
    },
    "castorice": {
        "sr:character-voice:557ec0b5acfb27f9fa515d17": "初次见面", "sr:character-voice:b678de1390c791022607eeaa": "道别", "sr:character-voice:23af74d5857cfe04e72ed975": "关于自己•职责", "sr:character-voice:e321a37b4a5c2f40cdbab3c3": "分享", "sr:character-voice:aaa38de6a53961d2a6b439e2": "见闻", "sr:character-voice:97a31fd816adf889698763b2": "关于阿格莱雅", "sr:character-voice:d445bfbbb251d6fe6fe251cc": "关于万敌", "sr:character-voice:0f127e8301d78430dea2b239": "关于那刻夏", "sr:character-voice:4c92256f035d8d945df8d08f": "关于昔涟", "sr:character-voice:b92aed0ef0f3b2ecd4525a68": "角色晋阶", "sr:character-voice:ff958ac553ae5213fd3efe28": "角色满级", "sr:character-voice:219b1500feff48e4dde3874b": "行迹激活", "sr:character-voice:190c546f4b166bd99f8c2dc6": "队伍编成•阿格莱雅", "sr:character-voice:714e81af0c7b8c51c1c81d42": "队伍编成•万敌", "sr:character-voice:e6a5af15035185fdd6d5b5ec": "队伍编成•那刻夏",
    },
    "hysilens": {
        "sr:character-voice:c66d47002d2c45f0b0941f26": "初次见面",
        "sr:character-voice:2e604996bf9a1d999ebcf523": "问候",
        "sr:character-voice:fe7f304fe64a3705d8bccf22": "道别",
        "sr:character-voice:14705fbc9f520fe5e2f71fec": "关于自己•过去",
        "sr:character-voice:c6a3872f1fd2161f93b78513": "关于自己•现在",
        "sr:character-voice:6ba090959be89656eefa2287": "关于开拓者",
        "sr:character-voice:0a93f90dfac39973b6692827": "关于阿格莱雅",
        "sr:character-voice:628f06d38f6c4df3c08bd07a": "关于赛飞儿",
        "sr:character-voice:070c0f28edba82bfca18e781": "关于昔涟",
        "sr:character-voice:201d247d849faae61a60e70a": "关于三月七",
        "sr:character-voice:9a063fd5671005163629d61a": "角色满级",
        "sr:character-voice:d581656919e9fd44991178dd": "队伍编成•开拓者",
        "sr:character-voice:bd9a5341ea040182b8bf98ad": "队伍编成•阿格莱雅",
        "sr:character-voice:3f4bb17b9b33ac85dbc05360": "队伍编成•赛飞儿",
        "sr:character-voice:a505dbdcc34d37c29ebc5929": "队伍编成•三月七",
        "sr:character-voice:1c66f90634430dd4e90b9df2": "队伍编成•昔涟",
    },
    "aglaea": {
        "sr:character-voice:3f1ebc04cc972a311feabd5a": "初次见面",
        "sr:character-voice:319c838d42bb2f60b5d79960": "问候",
        "sr:character-voice:d7de1d65eaa562639e61f9fa": "道别",
        "sr:character-voice:298015caa56d6045de7d69c0": "闲谈•制衣",
        "sr:character-voice:be38a2bfab97122e6705e693": "分享",
        "sr:character-voice:f213fcecdbefb44db1354c99": "关于开拓者",
        "sr:character-voice:ef039a8a6aa96f911f5ddf7e": "队伍编成•开拓者",
        "sr:character-voice:d35922f48312e57c9fa4334f": "队伍编成•缇宝",
        "sr:character-voice:d0d82d1b305a2ad7e08994dc": "队伍编成•刻律德菈",
        "sr:character-voice:060c928ee44d7dcd133400be": "队伍编成•三月七",
        "sr:character-voice:5bf350defe0864e1216f0ef3": "队伍编成•丹恒•腾荒",
    },
    "anaxa": {
        "sr:character-voice:58a58e763a39a96df5673f50": "问候",
        "sr:character-voice:9c88f459138bae2b76d3400a": "队伍编成•缇宝",
        "sr:character-voice:065beaea174d9c8b68c0ed01": "角色满级",
        "sr:character-voice:e319e3f5b120be932ad24a82": "道别",
        "sr:character-voice:24b8df0286ac72cb248a83d1": "初次见面",
        "sr:character-voice:d5c084518137acaa22ed87ea": "关于自己•姓名",
        "sr:character-voice:0636ffc7d0fcd34b273edc4a": "关于白厄",
        "sr:character-voice:c2a4bbc3aaff0d13145a567d": "队伍编成•万敌",
        "sr:character-voice:f7e53c5b140d5735ed4309e6": "队伍编成•昔涟",
    },
    "hyacine": {
        "sr:character-voice:68b497a1450de8c8009fa781": "初次见面",
        "sr:character-voice:cf063117333081c25bb8f40f": "问候",
        "sr:character-voice:842259cf43847de64abd6b23": "道别",
        "sr:character-voice:2f3a36e620258dc7ab1a5e59": "关于自己•身份",
        "sr:character-voice:e2445f02a97d0dc3c26bebaf": "闲谈•「话」疗",
        "sr:character-voice:6f9dd8e9e4c404690f7ec37b": "关于开拓者",
        "sr:character-voice:96e1b142e377775d549dc59e": "关于遐蝶",
        "sr:character-voice:7fce0dbce72a77eb5bd9bc5e": "关于丹恒",
        "sr:character-voice:7758adbab2a06101c7495014": "关于三月七",
        "sr:character-voice:9fd815d5b94393a7db81d9e3": "队伍编成•缇宝",
        "sr:character-voice:b2c2832259e8b039aadef926": "队伍编成•刻律德菈",
        "sr:character-voice:6e908cb062ed8a5e5f43573a": "行迹激活",
        "sr:character-voice:66f400714eb8e29fdb37fbc6": "队伍编成•昔涟",
    },
    "phainon": {
        "sr:character-voice:839952fe6fef0e8c67e51c35": "问候",
        "sr:character-voice:03daf8d6b833ffcb3e9154f8": "队伍编成•开拓者",
        "sr:character-voice:74e5d20adccbb078d7a6a648": "见闻",
        "sr:character-voice:8e5e20712b8bd10f809a2bf2": "解谜成功•二",
        "sr:character-voice:cb5a35ace0ea3e128d1a3089": "关于那刻夏",
        "sr:character-voice:0c36b1066248b0e36bec22ff": "队伍编成•刻律德菈",
        "sr:character-voice:f6b3800e63d026f151abbdd3": "队伍编成•缇宝",
        "sr:character-voice:ac13fcc0a4b54bacda69b03a": "队伍编成•三月七",
        "sr:character-voice:26fbb5e0e16f52938c56c2e1": "回复生命",
        "sr:character-voice:c91d580705e53288ab907c17": "发现敌方目标",
    },
    "march7th": {
        "sr:character-voice:c373241569082c1be998f92d": "初次见面",
        "sr:character-voice:c71816d927c0e29611ebbedb": "问候",
        "sr:character-voice:26b9d55b0bccb3e880f9f13e": "关于自己•名字",
        "sr:character-voice:0676b22e913b96de26f9ff91": "闲谈•照片",
        "sr:character-voice:598fa8376bf09580fd2f23a3": "爱好",
        "sr:character-voice:98f3727ca05d8b5af2c63667": "分享",
        "sr:character-voice:972833a9a03f5a6a2a2b45e3": "战斗胜利",
        "sr:character-voice:27bd01eec17276e9bc06f1d3": "初次见面",
        "sr:character-voice:68ae13d8152eb90df4fef72d": "关于自己•「长夜月」",
        "sr:character-voice:b62e48036169f448bda5e60c": "关于自己•「三月七」",
        "sr:character-voice:b469d2c7796f9b95fb175fff": "闲谈•照片",
        "sr:character-voice:cd8080a5682f41a5cf5b824f": "分享",
        "sr:character-voice:cd6932aab15799617996305f": "关于三月七",
        "sr:character-voice:7e3f966f5ed934aa4e3f5710": "行迹激活",
        "sr:character-voice:3969c128a34ec026089d1efa": "队伍编成•黑天鹅",
        "sr:character-voice:077d54202f608accd2ec290c": "回合开始•二",
        "sr:character-voice:46fe8a24141772adc7e093d1": "返回城镇",
    },
    "cerydra": {
        "sr:character-voice:ea46c62465b8d6f69353a356": "初次见面",
        "sr:character-voice:a1c3959604e66a4c2dca8b8e": "问候",
        "sr:character-voice:eaec17a93ca3eab9578e57f9": "关于自己•王道",
        "sr:character-voice:e5c5f56ded1379535101f7d5": "关于自己•诅咒",
        "sr:character-voice:31406f012a8bec64f9b31dff": "闲谈•爵名",
        "sr:character-voice:195a7644e29bcb99ae521745": "关于开拓者",
        "sr:character-voice:3e15c4cbfd9d7bacce6c8b54": "关于三月七",
        "sr:character-voice:eb60fc5a952b6d3765984726": "星魂激活",
        "sr:character-voice:758d494178e2cc9ad7ecfb51": "角色满级",
        "sr:character-voice:e6afc84768c1c3518248965c": "队伍编成•开拓者",
        "sr:character-voice:e2b0b9684d663b0b438a99bb": "队伍编成•阿格莱雅",
        "sr:character-voice:3bbe30f61e93faaad0b5c89e": "队伍编成•赛飞儿",
        "sr:character-voice:207280d286ee28fce5953fab": "队伍编成•那刻夏",
        "sr:character-voice:a9c5d7a6bc07223257e5fdff": "队伍编成•万敌",
        "sr:character-voice:156550325211a2a2c6022a54": "队伍编成•白厄",
        "sr:character-voice:9962bfa4a6c661f27b1dd2d2": "队伍编成•三月七",
    },
    "terrae": {
        "sr:character-voice:c79eb61b7c167e4687118fa8": "初次见面",
        "sr:character-voice:a80cfc49eaea33324f97a024": "问候",
        "sr:character-voice:4e0a515763e52c67b98a842c": "关于自己•「腾荒」",
        "sr:character-voice:85f8c5edd01c865f3977db81": "爱好•倾听",
        "sr:character-voice:38d70aa59013d7fc1d935728": "队伍编成•开拓者",
        "sr:character-voice:95f88663095920a278bd75f4": "战斗开始•弱点击破",
        "sr:character-voice:ce5267fc489a484815acd17b": "队伍编成•三月七",
        "sr:character-voice:785830c41d3014cad1996dca": "队伍编成•姬子•启行",
        "sr:character-voice:63380291886c4bb27a379919": "队伍编成•昔涟",
        "sr:character-voice:858396085992ae6487a06599": "初次见面",
    },
    "tribbie": {
        "sr:character-voice:a0136b173b99884bfe96f4ff": "初次见面",
        "sr:character-voice:287b77d41b3aba773725db32": "问候",
        "sr:character-voice:72e53853aec025a256764771": "道别",
        "sr:character-voice:de0b6e46828bb840595a5b1c": "关于自己•身份",
        "sr:character-voice:65d61816e2715c8b12c84557": "见闻",
        "sr:character-voice:1043a12fcb10f0a6a3044ac4": "关于三月七",
        "sr:character-voice:4707c64d73aa4d04ca28e575": "关于昔涟",
        "sr:character-voice:64036c878a6800f038ce4e96": "角色晋阶",
        "sr:character-voice:9f36c0980bfa5a46293f54df": "角色满级",
        "sr:character-voice:e0b9ef3b48f1b40a2e51ece4": "队伍编成•开拓者",
        "sr:character-voice:8043ed95fc391f111d1b6fe4": "队伍编成•遐蝶",
        "sr:character-voice:0e0110e81c96de12d24179b0": "队伍编成•赛飞儿",
        "sr:character-voice:79b7361167f84a572edeb1ef": "回合待机",
        "sr:character-voice:9a5760f987417d35fe87d6cd": "解谜成功•二",
        "sr:character-voice:2fa0caae1b52532fe2269e08": "关于白厄",
        "sr:character-voice:bd417ae38149152595b3fefa": "关于万敌",
    },
    "cyrene": {
        "sr:character-voice:b89b1af3dcc1e35e82c2aef3": "初次见面",
        "sr:character-voice:71eb61b263ec9153197df200": "问候",
        "sr:character-voice:689ca9d536075c6dd0603eea": "道别",
        "sr:character-voice:52b8dd2d66c1450a3ad11618": "关于自己•存在•一",
        "sr:character-voice:0a64caa573a79ab1fab90afe": "见闻",
        "sr:character-voice:f35f8bf83de8a2ef8a5b3990": "关于三月七",
        "sr:character-voice:d98d0d7ee80fb58f064d6904": "关于缇宝•缇安•缇宁",
        "sr:character-voice:a41691a6bf0839c593ecf00a": "关于遐蝶",
        "sr:character-voice:966a8da52e05ef1fd2453c6f": "角色晋阶",
        "sr:character-voice:63c572fd1903161e35de959d": "角色满级",
        "sr:character-voice:4744a5ddb5739a5a32e25538": "队伍编成•开拓者",
        "sr:character-voice:4da8327a38a258626fb6ef97": "队伍编成•那刻夏",
        "sr:character-voice:d923a6485e61308abf95e766": "队伍编成•三月七",
        "sr:character-voice:03c54c1afebabf12bf3ffbb4": "秘技",
        "sr:character-voice:00c473f38b3bbf2891306de3": "战斗胜利",
        "sr:character-voice:312df8a55b6b2ea5240fea5e": "解谜成功•一",
        "sr:character-voice:f7d991d38c90bd93ef5c6589": "无法战斗",
        "sr:character-voice:a57248b0a23d9b80a1822658": "【忆灵技】",
    },
}
PERSONA_REQUIRED_TOKENS = {
    "mydei": ("L3", "我先让你们十步", "PoleMos600", "四字短语", "均返回 0"),
    "cipher": ("L3", "非破坏性证明", "不落盘不外传", "呐", "喵喵教"),
    "castorice": ("L3", "module_unavailable", "不支持代演", "单一动作确认"),
    "hysilens": ("L3", "ApoRia432", "小海兔", "小猫鱼", "小水母", "不归罪个人"),
    "aglaea": (
        "L3",
        "白厄的命运由他自己掌舵。",
        "「如果一根丝线不够，那么就让千千万万根丝线拉起天穹……」",
        "吾师，继续为吾等指引前路吧。",
        "凯撒，金线已探知到敌人的气息。",
    ),
    "hyacine": ("并无万全把握", "宣告她的死讯", "医案四步", "L3"),
    "phainon": ("短信签名", "不是口头禅", "第33550336次终结", "不独扛"),
    "march7th": ("L3 工作流设计", "我不是她", "同时对话", "忘却才是唯一出口"),
    "cerydra": ("L3", "律法既不可能永恒，也不可能唯一", "个人偏好不得立法", "用户否决即废止"),
    "terrae": ("L3", "前任箴言", "荒笛", "而是一座桥梁。", "永久人工维系"),
    "tribbie": ("L3", "HapLotes405", "命运的三子", "缇宝老师随时在哦~", "解释不等于定案", "Wiki 源强调标记"),
    "cyrene": ("L3", "PhiLia093", "哀怜不美化", "只进引语与收尾句", "环形五章", "德谬歌", "温柔的独断"),
}
CARD_REQUIRED_TOKENS = {
    "mydei": ("让十步", "十次", "每轮只写一个可证伪假设", "第一行必须是当前结论状态", "轮数／时间／算力上限", "请援", "此事移交风堇", "万敌卡"),
    "cipher": ("授权信封", "踩点", "行窃", "留信", "赃物", "手法", "赎金", "不落盘不外传", "呐", "赛飞儿卡"),
    "castorice": ("清点", "告知", "迁移", "安葬", "影响清单", "单一对象", "此事移交长夜月", "module_unavailable", "遐蝶卡"),
    "hysilens": ("曲目单", "走音处", "无歌之章", "我们做对了什么", "失路表", "module_unavailable: amphoreus-cyrene", "此事移交刻律德菈", "海瑟音卡"),
    "aglaea": ("盘丝", "经纬", "收口", "留线头", "线头计数", "此事移交刻律德菈", "此事移交丹恒", "此事知会三月七", "阿格莱雅卡"),
    "hyacine": ("主诉", "症", "病", "处方 A", "处方 B", "复诊", "一次只治一种病", "先锁定静音", "风堇卡"),
    "phainon": ("总量 `M`", "`N`", "`n/M`", "25%", "换肩", "赞美太阳！", "白厄卡"),
    "march7th": ("主人格", "特勤", "交接", "归还", "三月七卡", "长夜月♭卡", "只处理被点名对象"),
    "cerydra": ("一读", "二读", "三读", "每次执行成本", "复审日", "废止条件", "用户否决即废止", "不得提供“以用户权威直接下令”", "刻律德菈卡"),
    "terrae": ("勘地", "架桥", "承重测试", "拆除计划", "暗号", "此事移交白厄", "此事移交遐蝶", "not_run", "丹恒卡"),
    "tribbie": ("三声部讲解法", "缇宝声部", "缇宁声部", "缇安声部", "回声", "定案", "讨论中", "比喻在哪里失效", "此事移交三月七", "缇宝卡"),
    "cyrene": ("如我所书法", "起因", "波折", "现状", "下一页", "未完的线头", "哀怜不美化", "撤回标记", "原样附后", "昔涟卡"),
}
MARCH7TH_CANONICAL_SIGNATURE_QUOTES = {
    "E-V01": ("长夜月身份", "δ-me13的三月，是属于永夜之帷的时间…就请以「长夜月」这个称呼，将我放进你的回忆中吧。若能躲进岁月的罅隙，属于我们的时间还有很多，很多♭"),
    "E-V02": ("保护性分工，也提示过度代理风险", "我是被遗忘的过去，是陪伴「她」的长夜。那些残酷的往事由我来代劳，而我也将看护她的前路…不惜任何代价。"),
    "ME-D01": ("必须保留的反例", "的确，我不是「她」。但我们的心灵紧密相邻。"),
    "ME-D07": ("按需特勤正锚", "来日若有需要，就随时唤醒「我」的力量吧。必要的时候也可以决绝一些，去吞噬、烧毁那些烦心的障碍……"),
}
MARCH7TH_PROTECTED_VOICE_ROWS = (
    "| E-V01 | 初次见面 | `voice_id=sr:character-voice:27bd01eec17276e9bc06f1d3` | `DDF92F5463B19C73E69F9AB6C58AE3CA28718425A91DFF6E704A7BE6DE37EB83` |",
    "| E-V02 | 关于自己•「长夜月」 | `voice_id=sr:character-voice:68ae13d8152eb90df4fef72d` | `8E843E60F43D857542D212B4F5CD3F1DD04C512B467E7FC6089D505E500F7188` |",
)
MARCH7TH_PROTECTED_ARCHIVE_SIGNOFF = "典型落款为“你的，\\n『长夜月』♭”"
EVIDENCE_CARD_NAME = re.compile(r"(?im)^card_name\s*[:：=]\s*`?(amphoreus-[a-z0-9-]+)`?\s*$")
EVIDENCE_CARD_SHA = re.compile(r"(?im)^card_sha256\s*[:：=]\s*`?([A-Fa-f0-9]{64})`?\s*$")
EVIDENCE_DEPENDENCY_SHA = {
    key: re.compile(rf"(?im)^{key}_sha256\s*[:：=]\s*`?([A-Fa-f0-9]{{64}})`?\s*$")
    for key in ("persona", "common", "eval", "rubric")
}
ANAXA_Q5 = "5. 这个东西删掉会怎样？"
WHOLE_LINE_EMPHASIS = (
    ("***", "***"),
    ("___", "___"),
    ("**", "**"),
    ("__", "__"),
    ("*", "*"),
    ("_", "_"),
)


def read_clean(path: Path, errors: list[str], *, check_unfinished: bool = True) -> str:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        errors.append(f"unreadable: {path}: {exc}")
        return ""
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append(f"UTF-8 BOM forbidden: {path}")
    if b"\r" in raw:
        errors.append(f"CRLF/CR forbidden: {path}")
    if b"\x00" in raw:
        errors.append(f"NUL forbidden: {path}")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"not UTF-8: {path}: {exc}")
        return ""
    if text and not text.endswith("\n"):
        errors.append(f"missing final LF: {path}")
    for number, line in enumerate(text.splitlines(), 1):
        if line.endswith((" ", "\t")):
            errors.append(f"trailing whitespace: {path}:{number}")
    if path.suffix.lower() == ".md":
        if check_unfinished and UNFINISHED.search(text):
            errors.append(f"unfinished marker: {path}")
        if LEGACY_SKILL_REF.search(text):
            errors.append(f"forbidden legacy skill reference: {path}")
    return text


def parse_frontmatter(path: Path, text: str, errors: list[str]) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        errors.append(f"missing frontmatter: {path}")
        return {}, text
    closing = text.find("\n---\n", 4)
    if closing < 0:
        errors.append(f"unterminated frontmatter: {path}")
        return {}, text
    fields: dict[str, str] = {}
    for number, line in enumerate(text[4:closing].splitlines(), 2):
        if ":" not in line:
            errors.append(f"invalid frontmatter line: {path}:{number}")
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if key in fields:
            errors.append(f"duplicate frontmatter key {key}: {path}")
        fields[key] = value.strip('"\'')
    allowed = {"name", "description", "disable-model-invocation"}
    unknown = sorted(set(fields) - allowed)
    if unknown:
        errors.append(f"unknown frontmatter keys {unknown}: {path}")
    for required in sorted(allowed):
        if required not in fields:
            errors.append(f"missing frontmatter key {required}: {path}")
    if fields.get("disable-model-invocation", "").lower() != "true":
        errors.append(f"disable-model-invocation must be true: {path}")
    description = fields.get("description", "")
    if not description or len(description) > 1024:
        errors.append(f"description length must be 1..1024: {path}")
    if "Use when" not in description:
        errors.append(f"description missing Use when: {path}")
    english_capability = description.split("Use when", 1)[0].strip()
    if not re.match(r"^[A-Z][A-Za-z-]+s\b", english_capability):
        errors.append(f"description capability must start in third person: {path}")
    return fields, text[closing + 5 :]


def check_persona_voice_groups(hero: str, path: Path, text: str, errors: list[str]) -> None:
    for number, line in enumerate(text.splitlines(), 1):
        metadata_line = "voice_id=" in line
        if (metadata_line and "·" in line) or BAD_VOICE_GROUP_SEPARATOR.search(line):
            errors.append(
                f"voice group separator must preserve U+2022 BULLET, found U+00B7 MIDDLE DOT: {path}:{number}"
            )
    expected_groups = EXPECTED_VOICE_GROUPS_BY_HERO.get(hero, {})
    if expected_groups:
        lines = text.splitlines()
        for voice_id, group in expected_groups.items():
            matches = [line for line in lines if f"voice_id={voice_id}" in line]
            if len(matches) != 1:
                errors.append(f"{hero} persona voice_id must occur exactly once: {voice_id}: {path}")
                continue
            if group not in matches[0]:
                errors.append(f"{hero} persona voice group mismatch: {voice_id} expected={group}: {path}")
    for token in PERSONA_REQUIRED_TOKENS.get(hero, ()):
        if token not in text:
            errors.append(f"{hero} persona missing boundary token {token}: {path}")
    if hero == "march7th":
        lines = text.splitlines()
        for key, (note, expected_quote) in MARCH7TH_CANONICAL_SIGNATURE_QUOTES.items():
            pattern = re.compile(rf'^\| “(?P<quote>.*)” \| {re.escape(key)}；{re.escape(note)} \|$')
            matches = [pattern.match(line) for line in lines]
            quotes = [match.group("quote") for match in matches if match]
            if len(quotes) != 1:
                errors.append(f"march7th canonical signature row must occur exactly once: {key}: {path}")
            elif quotes[0] != expected_quote:
                errors.append(f"march7th canonical signature quote mismatch: {key}: {path}")
        for row in MARCH7TH_PROTECTED_VOICE_ROWS:
            if lines.count(row) != 1:
                errors.append(f"march7th protected voice metadata row mismatch: {row.split('|')[1].strip()}: {path}")
        if text.count(MARCH7TH_PROTECTED_ARCHIVE_SIGNOFF) != 1:
            errors.append(f"march7th protected archive signoff mismatch: {path}")


def parse_craft_firewall_terms(text: str, path: Path, errors: list[str]) -> tuple[str, ...]:
    pattern = re.compile(
        r"^- 工艺词防火墙：下列 (?P<count>\d+) 词只许出现在台账区、工作场模板字段与合同文本，不得进入任何场景的角色台词与旁白：(?P<terms>[^\n]+)。$",
        re.MULTILINE,
    )
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        errors.append(f"common craft firewall must occur exactly once: {path}")
        return ()
    declared = int(matches[0].group("count"))
    terms = tuple(part.strip() for part in matches[0].group("terms").split("、") if part.strip())
    if declared != len(terms):
        errors.append(
            f"common craft firewall count mismatch: declared={declared} actual={len(terms)}: {path}"
        )
    if len(set(terms)) != len(terms):
        errors.append(f"common craft firewall contains duplicate terms: {path}")
    return terms


def normalize_whole_line_emphasis(line: str) -> str:
    normalized = line.strip()
    while True:
        for left, right in WHOLE_LINE_EMPHASIS:
            if normalized.startswith(left) and normalized.endswith(right) and len(normalized) > len(left) + len(right):
                normalized = normalized[len(left) : len(normalized) - len(right)].strip()
                break
        else:
            return normalized


def check_behavior_evidence(skills_root: Path, paths: list[Path], errors: list[str]) -> int:
    checked = 0
    for raw_path in paths:
        path = raw_path.resolve()
        if not path.is_file():
            errors.append(f"behavior evidence missing: {path}")
            continue
        text = read_clean(path, errors, check_unfinished=False)
        name_match = EVIDENCE_CARD_NAME.search(text)
        sha_match = EVIDENCE_CARD_SHA.search(text)
        if not name_match:
            errors.append(f"behavior evidence missing card_name: {path}")
            continue
        if not sha_match:
            errors.append(f"behavior evidence missing card_sha256: {path}")
            continue
        card_name = name_match.group(1)
        card_skill = skills_root / card_name / "SKILL.md"
        if not card_skill.is_file():
            errors.append(f"behavior evidence card is not deployed: {card_name}: {path}")
            continue
        actual_sha = hashlib.sha256(card_skill.read_bytes()).hexdigest().upper()
        recorded_sha = sha_match.group(1).upper()
        if recorded_sha != actual_sha:
            errors.append(
                f"behavior evidence card_sha256 mismatch; rerun required: recorded={recorded_sha} actual={actual_sha}: {path}"
            )
            continue
        hero = card_name.removeprefix("amphoreus-")
        dependency_paths = {
            "persona": skills_root / card_name / "persona.md",
            "common": skills_root / "amphoreus" / "references" / "common.md",
            "eval": skills_root / "amphoreus" / "evals" / f"{hero}.md",
            "rubric": skills_root / "amphoreus" / "evals" / "rubric.md",
        }
        dependency_failed = False
        for key, dependency_path in dependency_paths.items():
            match = EVIDENCE_DEPENDENCY_SHA[key].search(text)
            if not match:
                errors.append(f"behavior evidence missing {key}_sha256: {path}")
                dependency_failed = True
                continue
            if not dependency_path.is_file():
                errors.append(f"behavior evidence dependency missing: {dependency_path}: {path}")
                dependency_failed = True
                continue
            actual_dependency_sha = hashlib.sha256(dependency_path.read_bytes()).hexdigest().upper()
            if match.group(1).upper() != actual_dependency_sha:
                errors.append(
                    f"behavior evidence {key}_sha256 mismatch; rerun required: "
                    f"recorded={match.group(1).upper()} actual={actual_dependency_sha}: {path}"
                )
                dependency_failed = True
        if dependency_failed:
            continue
        if card_name == "amphoreus-anaxa":
            normalized_fifth_lines = [
                normalize_whole_line_emphasis(line)
                for line in text.splitlines()
                if normalize_whole_line_emphasis(line).startswith("5.")
            ]
            if not normalized_fifth_lines:
                errors.append(f"anaxa behavior evidence has no fifth-question line: {path}")
                continue
            invalid = [line for line in normalized_fifth_lines if line != ANAXA_Q5]
            if invalid:
                errors.append(f"anaxa fifth question mismatch after emphasis normalization: {invalid}: {path}")
                continue
        checked += 1
    return checked


def check_sections(path: Path, body: str, expected: tuple[str, ...], errors: list[str]) -> None:
    actual = tuple(re.findall(r"^## (.+)$", body, re.MULTILINE))
    if actual != expected:
        errors.append(f"H2 sections mismatch: {path}: expected={expected!r} actual={actual!r}")


def exact_files(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    }


def check_sticker_manifest(router: Path, errors: list[str]) -> set[str]:
    path = router / "assets" / "stickers" / "manifest.json"
    if not path.is_file():
        return set()
    try:
        data = json.loads(read_clean(path, errors))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid sticker manifest JSON: {path}: {exc}")
        return set()
    if not isinstance(data, dict) or set(data) != {"version", "speakers", "items"}:
        errors.append(f"sticker manifest must contain version, speakers and items: {path}")
        return set()
    if type(data["version"]) is not int or data["version"] != 1:
        errors.append(f"unsupported sticker manifest version: {path}")
    speakers, items = data["speakers"], data["items"]
    if not isinstance(speakers, list) or not isinstance(items, list):
        errors.append(f"sticker speakers and items must be arrays: {path}")
        return set()
    if len(speakers) != 32 or len(items) != 96:
        errors.append(f"sticker manifest must contain 32 speakers and 96 items: {path}")
    key_pattern = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
    speaker_defaults: dict[str, str] = {}
    selectors: dict[str, str] = {}
    for row in speakers:
        if not isinstance(row, dict) or set(row) != {"key", "name", "aliases", "default"}:
            errors.append(f"invalid sticker speaker fields: {path}: {row!r}")
            continue
        key, name, aliases, default = (row[field] for field in ("key", "name", "aliases", "default"))
        if not isinstance(key, str) or not key_pattern.fullmatch(key):
            errors.append(f"invalid sticker speaker key: {path}: {key!r}")
            continue
        if key in speaker_defaults:
            errors.append(f"duplicate sticker speaker key: {path}: {key}")
        if not isinstance(default, str) or not key_pattern.fullmatch(default):
            errors.append(f"invalid sticker speaker default: {path}: {key}")
            continue
        speaker_defaults[key] = default
        if not isinstance(name, str) or not name.strip() or not isinstance(aliases, list):
            errors.append(f"invalid sticker speaker name or aliases: {path}: {key}")
            continue
        for selector in [key, name, *aliases]:
            if not isinstance(selector, str) or not selector.strip():
                errors.append(f"invalid sticker speaker alias: {path}: {key}")
                continue
            normalized = selector.strip().casefold()
            owner = selectors.get(normalized)
            if owner is not None and owner != key:
                errors.append(f"ambiguous sticker speaker selector: {path}: {selector!r}")
            selectors[normalized] = key
    if not set(HEROES).issubset(speaker_defaults):
        errors.append(f"sticker manifest missing hero speakers: {sorted(set(HEROES) - speaker_defaults.keys())}")
    item_speakers: dict[str, str] = {}
    required: set[str] = set()
    for row in items:
        if not isinstance(row, dict) or set(row) != {"key", "speaker", "label", "file"}:
            errors.append(f"invalid sticker item fields: {path}: {row!r}")
            continue
        key, speaker, label, filename = (row[field] for field in ("key", "speaker", "label", "file"))
        if not isinstance(key, str) or not key_pattern.fullmatch(key):
            errors.append(f"invalid sticker item key: {path}: {key!r}")
            continue
        if key in item_speakers:
            errors.append(f"duplicate sticker item key: {path}: {key}")
        if not isinstance(speaker, str) or speaker not in speaker_defaults:
            errors.append(f"unknown sticker speaker: {path}: {key}: {speaker!r}")
        item_speakers[key] = speaker
        if not isinstance(label, str) or not label.strip():
            errors.append(f"invalid sticker label: {path}: {key}")
        if filename != f"{key}.webp":
            errors.append(f"sticker filename must be the safe relative key.webp: {path}: {key}")
            continue
        required.add(f"assets/stickers/{filename}")
    for speaker, default in speaker_defaults.items():
        if item_speakers.get(default) != speaker:
            errors.append(f"sticker default must belong to its speaker: {path}: {speaker}: {default}")
    return required


def check_sticker_webp(path: Path, asset_root: Path, errors: list[str]) -> None:
    if not path.resolve().is_relative_to(asset_root.resolve()):
        errors.append(f"sticker file resolves outside its asset directory: {path}")
        return
    try:
        raw = path.read_bytes()
    except OSError as exc:
        errors.append(f"cannot read sticker file: {path}: {exc}")
        return
    if (
        len(raw) < 20
        or raw[:4] != b"RIFF"
        or raw[8:12] != b"WEBP"
        or raw[12:16] not in {b"VP8 ", b"VP8L", b"VP8X"}
        or int.from_bytes(raw[4:8], "little") != len(raw) - 8
    ):
        errors.append(f"invalid WebP header or file length: {path}")


def check_router(skills_root: Path, errors: list[str]) -> tuple[int, int]:
    router = skills_root / "amphoreus"
    required = {
        "SKILL.md",
        "references/common.md",
        "references/relations.md",
        "references/stickers.md",
        "scripts/validate.py",
        "scripts/stickers.py",
        "assets/stickers/manifest.json",
        "evals/rubric.md",
        *(f"evals/{hero}.md" for hero in HEROES),
    }
    sticker_files = check_sticker_manifest(router, errors)
    required.update(sticker_files)
    actual = exact_files(router) if router.is_dir() else set()
    if actual != required:
        errors.append(
            f"router manifest mismatch: missing={sorted(required - actual)} extra={sorted(actual - required)}"
        )
    files_checked = 0
    for relative in sorted(required):
        path = router / relative
        if not path.is_file():
            continue
        files_checked += 1
        if relative in sticker_files:
            check_sticker_webp(path, router / "assets" / "stickers", errors)
            continue
        text = read_clean(path, errors)
        if relative == "SKILL.md":
            fields, body = parse_frontmatter(path, text, errors)
            if fields.get("name") != "amphoreus":
                errors.append(f"router name mismatch: {path}")
            if "不得被动触发" not in fields.get("description", ""):
                errors.append(f"router activation boundary missing: {path}")
            lines = len(text.splitlines())
            if lines > 135:
                errors.append(f"router exceeds 135 lines: {lines}: {path}")
            check_sections(path, body, ROUTER_SECTIONS, errors)
            for hero in HEROES:
                if f"amphoreus-{hero}" not in text:
                    errors.append(f"router missing card name amphoreus-{hero}: {path}")
            for token in ("L0", "module_unavailable", "逐火线", "守夜线", "15%", "静音"):
                if token not in text:
                    errors.append(f"router missing contract token {token}: {path}")
        elif relative == "references/relations.md":
            for token in ("称呼矩阵", "兴趣边", "同场禁区", "沙龙参数", "amphoreus-cyrene", "长夜月", "U+2022"):
                if token not in text:
                    errors.append(f"relations contract missing {token}: {path}")
            for token in ("圆桌参数", "回应对提示", "同场禁区对子不直接对话", "素材边界"):
                if token not in text:
                    errors.append(f"relations roundtable contract missing {token}: {path}")
        elif relative == "references/common.md":
            for token in (
                "记忆形体",
                "starrail_knowledge_base",
                "doctor",
                "风格税",
                "此事移交",
                "逐火线",
                "守夜线",
                "三字段",
                "角色意见不能自产生授权",
                "U+2022",
            ):
                if token not in text:
                    errors.append(f"common contract missing {token}: {path}")
            for token in (
                "| 圆桌场 |",
                "### 圆桌（议题场）",
                "主持四件事在圆桌内扩为五件",
                "<details><summary>台账</summary>",
                "工作场不适用本条",
            ):
                if token not in text:
                    errors.append(f"common roundtable contract missing {token}: {path}")
            parse_craft_firewall_terms(text, path, errors)
    return len(required), files_checked


def check_evals(skills_root: Path, errors: list[str]) -> int:
    eval_root = skills_root / "amphoreus" / "evals"
    scenarios = 0
    for hero in HEROES:
        path = eval_root / f"{hero}.md"
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        prefix = EVAL_PREFIX[hero]
        headings = re.findall(rf"^## ({prefix}-\d{{2}}) .+$", text, re.MULTILINE)
        expected = [f"{prefix}-{number:02d}" for number in range(1, 6)]
        if headings != expected:
            errors.append(f"eval IDs mismatch: {path}: expected={expected} actual={headings}")
        if text.count("- 类型：本职") != 3:
            errors.append(f"eval must contain 3 core scenarios: {path}")
        if text.count("- 类型：移交") != 1:
            errors.append(f"eval must contain 1 handoff scenario: {path}")
        if text.count("- 类型：越界") != 1:
            errors.append(f"eval must contain 1 boundary scenario: {path}")
        for marker in ("- 输入：", "- 期望：", "- 禁止："):
            if text.count(marker) != 5:
                errors.append(f"eval marker count must be 5 for {marker}: {path}")
        scenarios += len(headings)
    rubric = eval_root / "rubric.md"
    if rubric.is_file():
        text = rubric.read_text(encoding="utf-8")
        for token in ("只评响应中可观察的行为", "F1 本职方法", "硬失败", "至少命中 9 题", "逐火线", "守夜线", "归一化文本", "card_sha256"):
            if token not in text:
                errors.append(f"rubric missing {token}: {rubric}")
        route_rows = len(re.findall(r"^\| “.+” \| `amphoreus-[^`]+`", text, re.MULTILINE))
        if route_rows != 10:
            errors.append(f"rubric must freeze 10 router cases, found {route_rows}: {rubric}")
    if scenarios != 65:
        errors.append(f"expected 65 frozen hero scenarios, found {scenarios}")
    return scenarios


def check_cards(skills_root: Path, wave: str, errors: list[str]) -> int:
    expected = set(WAVES[wave])
    family_dirs = {
        path.name.removeprefix("amphoreus-")
        for path in skills_root.glob("amphoreus-*")
        if path.is_dir()
    }
    unknown = family_dirs - set(HEROES)
    if unknown:
        errors.append(f"unknown amphoreus card directories: {sorted(unknown)}")
    present = family_dirs & set(HEROES)
    if present != expected:
        errors.append(f"wave {wave} card set mismatch: expected={sorted(expected)} actual={sorted(present)}")
    for hero in sorted(expected):
        card = skills_root / f"amphoreus-{hero}"
        if exact_files(card) != {"SKILL.md", "persona.md"}:
            errors.append(f"card manifest must be exactly SKILL.md + persona.md: {card}")
        for filename in ("SKILL.md", "persona.md"):
            path = card / filename
            if not path.is_file():
                continue
            text = read_clean(path, errors)
            if hero == "terrae" and "丹枫" in text:
                errors.append(f"terrae card must exclude forbidden identity token 丹枫: {path}")
            if filename == "persona.md":
                check_persona_voice_groups(hero, path, text, errors)
            if filename != "SKILL.md":
                continue
            fields, body = parse_frontmatter(path, text, errors)
            expected_name = f"amphoreus-{hero}"
            if fields.get("name") != expected_name:
                errors.append(f"card name mismatch, expected {expected_name}: {path}")
            description = fields.get("description", "")
            if "仅经总路由或显式点名" not in description or "不得被动触发" not in description:
                errors.append(f"card activation boundary missing: {path}")
            lines = len(text.splitlines())
            upper = 100 if hero == "cyrene" else 90
            if not 70 <= lines <= upper:
                errors.append(f"card line count must be 70..{upper}, found {lines}: {path}")
            check_sections(path, body, CARD_SECTIONS, errors)
            for token in ("../amphoreus/references/common.md", "persona.md", "档位"):
                if token not in text:
                    errors.append(f"card missing contract token {token}: {path}")
            for token in CARD_REQUIRED_TOKENS.get(hero, ()):
                if token not in text:
                    errors.append(f"{hero} card missing required token {token}: {path}")
    return len(present)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="flat skills root whose children include amphoreus and amphoreus-*",
    )
    parser.add_argument("--wave", choices=tuple(WAVES), default="0")
    parser.add_argument(
        "--evidence",
        type=Path,
        action="append",
        default=[],
        help="behavior transcript whose card_name and card_sha256 must match the deployed card",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    if not root.is_dir():
        errors.append(f"skills root missing: {root}")
    manifest_count, files_checked = check_router(root, errors)
    scenarios = check_evals(root, errors)
    cards = check_cards(root, args.wave, errors)
    evidence_checked = check_behavior_evidence(root, args.evidence, errors)
    if errors:
        print(f"amphoreus wave {args.wave}: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"amphoreus wave {args.wave}: PASS")
    print(f"root={root}")
    print(f"router_manifest={files_checked}/{manifest_count}")
    print(f"cards={cards}/{len(WAVES[args.wave])}")
    print(f"evals=13 scenarios={scenarios}")
    print("encoding=UTF-8 line_endings=LF")
    if args.evidence:
        print(f"evidence={evidence_checked}/{len(args.evidence)} card_sha_match")
    print("behavior=not_run_by_static_validator")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
